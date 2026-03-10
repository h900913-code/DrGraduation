from __future__ import annotations

import csv
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import fitz
import requests


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Potential Papers"
DATA = BASE / "data"
REGION_BASE = BASE / "by_region"
PDF_DIR = REGION_BASE / "pdf_region"
TEXT_DIR = DATA / "text"
RANKED = DATA / "candidate_ranked.csv"
MANIFEST = DATA / "papers_manifest.csv"
MANUAL_LOG = DATA / "manual_download_log.json"
RUN_LOG = DATA / "additional_download_log.json"

UA = "PotentialPapersCollector/1.0 (additional-20)"


CLIMATE_TERMS = [
    "climate",
    "global warming",
    "environment",
    "carbon",
    "sustainab",
]

COMM_TERMS = [
    "communication",
    "social media",
    "youtube",
    "video",
    "comment",
    "discourse",
    "framing",
    "misinformation",
    "skeptic",
    "polarization",
    "public",
    "engagement",
    "twitter",
    "facebook",
    "reddit",
    "tiktok",
    "weibo",
]

NEGATIVE_HINTS = [
    "battery",
    "photovoltaic",
    "soil",
    "geology",
    "hydrology",
    "nanoparticle",
    "compressive strength",
    "cement",
    "machine fault",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def title_norm(text: str) -> str:
    return re.sub(r"\W+", "", (text or "").lower())


def is_mdpi(row: dict[str, str]) -> bool:
    blob = " ".join(
        [
            row.get("publisher", ""),
            row.get("pdf_host", ""),
            row.get("landing_url", ""),
            row.get("pdf_url", ""),
            row.get("journal", ""),
            row.get("title", ""),
        ]
    ).lower()
    return "mdpi" in blob or "mdpi.com" in blob


def safe(text: str, limit: int = 120) -> str:
    text = (text or "").replace(":", " - ")
    for ch in '\\/*?"<>|':
        text = text.replace(ch, "")
    text = " ".join(text.split()).strip().strip(".")
    return text[:limit].rstrip()


def build_filename(row: dict[str, str]) -> str:
    authors = [x.strip() for x in (row.get("authors") or "").split(";") if x.strip()]
    if not authors:
        author_part = "Unknown Author"
    elif len(authors) == 1:
        author_part = authors[0]
    elif len(authors) == 2:
        author_part = f"{authors[0]}, & {authors[1]}"
    else:
        author_part = f"{authors[0]}, et al."
    year = row.get("year") or "n.d."
    title = row.get("title") or "Untitled"
    journal = row.get("journal") or "Unknown Journal"
    return f"{safe(author_part, 80)} ({year}). {safe(title, 130)}. {safe(journal, 80)}.pdf"


def unique_pdf_name(filename: str) -> str:
    base = Path(filename).stem
    ext = Path(filename).suffix or ".pdf"
    candidate = filename
    n = 2
    while (PDF_DIR / candidate).exists():
        candidate = f"{base} [{n}]{ext}"
        n += 1
    return candidate


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_json_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        return obj if isinstance(obj, list) else []
    except Exception:
        return []


def save_json(path: Path, data: list[dict]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def topical_score(row: dict[str, str]) -> tuple[int, int, int]:
    blob = " ".join(
        [
            row.get("title", ""),
            row.get("journal", ""),
            row.get("matched_queries", ""),
            row.get("relation_type", ""),
        ]
    ).lower()
    climate_hits = sum(1 for t in CLIMATE_TERMS if t in blob)
    comm_hits = sum(1 for t in COMM_TERMS if t in blob)
    negative_hits = sum(1 for t in NEGATIVE_HINTS if t in blob)

    try:
        rel = float(row.get("relevance_score") or 0.0)
    except Exception:
        rel = 0.0
    try:
        year = int(row.get("year") or 0)
    except Exception:
        year = 0

    score = int(rel)
    score += climate_hits * 9
    score += comm_hits * 7
    if "youtube" in blob:
        score += 7
    if row.get("relation_type", "").lower() == "direct":
        score += 8
    if year >= 2020:
        score += 3
    if year >= 2023:
        score += 2
    score -= negative_hits * 10
    return score, climate_hits, comm_hits


def normalize_doi(raw: str) -> str:
    raw = (raw or "").strip()
    m = re.search(r"(10\.[^/\s]+/.+)$", raw, flags=re.IGNORECASE)
    if m:
        return m.group(1).rstrip(" .")
    return ""


def url_candidates(row: dict[str, str]) -> list[str]:
    urls: list[str] = []

    for key in ["pdf_url", "landing_url"]:
        u = (row.get(key) or "").strip()
        if u and u not in urls:
            urls.append(u)

    landing = (row.get("landing_url") or "").strip()
    if landing:
        if "/article/" in landing:
            u = landing.rstrip("/") + "/pdf"
            if u not in urls:
                urls.append(u)
        if "tandfonline.com/doi/full/" in landing:
            u = landing.replace("/doi/full/", "/doi/pdf/")
            if u not in urls:
                urls.append(u)
        if "journals.sagepub.com/doi/full/" in landing:
            u = landing.replace("/doi/full/", "/doi/pdf/")
            if u not in urls:
                urls.append(u)
        if "link.springer.com/article/" in landing:
            u = landing.rstrip("/") + ".pdf"
            if u not in urls:
                urls.append(u)
        if "nature.com/articles/" in landing and not landing.endswith(".pdf"):
            u = landing.rstrip("/") + ".pdf"
            if u not in urls:
                urls.append(u)

    doi = normalize_doi(row.get("doi", "") or landing)
    if doi:
        doi_url = f"https://doi.org/{doi}"
        if doi_url not in urls:
            urls.append(doi_url)

    return urls


def is_pdf_response(resp: requests.Response) -> bool:
    ctype = (resp.headers.get("content-type") or "").lower()
    if "pdf" in ctype:
        return True
    return resp.content[:8].startswith(b"%PDF")


def discover_pdf_link(html_text: str, base_url: str) -> str:
    for m in re.finditer(r"""href=['"]([^'"]+\.pdf(?:\?[^'"]*)?)['"]""", html_text, flags=re.IGNORECASE):
        return urljoin(base_url, m.group(1))
    return ""


def fetch_pdf(session: requests.Session, row: dict[str, str]) -> tuple[bytes | None, str, str]:
    last_detail = "no_url"
    tried = []
    for u in url_candidates(row):
        if not u or u in tried:
            continue
        tried.append(u)
        try:
            r = session.get(u, timeout=75, allow_redirects=True)
            if r.status_code != 200:
                last_detail = f"HTTP {r.status_code} {u}"
                continue
            if is_pdf_response(r):
                return r.content, u, "ok"

            ctype = (r.headers.get("content-type") or "").lower()
            if "html" in ctype:
                html = r.text[:250000]
                linked = discover_pdf_link(html, str(r.url))
                if linked and linked not in tried:
                    tried.append(linked)
                    r2 = session.get(linked, timeout=75, allow_redirects=True)
                    if r2.status_code == 200 and is_pdf_response(r2):
                        return r2.content, linked, "ok_html_discovered"
                    last_detail = f"html_link_non_pdf {linked} ({r2.status_code})"
                    continue
            last_detail = f"non_pdf_response {u} ({ctype[:80]})"
        except Exception as exc:
            last_detail = f"{u} -> {type(exc).__name__}: {exc}"
    return None, "", last_detail


def extract_text(pdf_path: Path, txt_path: Path, max_pages: int = 120) -> tuple[int, int]:
    doc = fitz.open(pdf_path)
    pages = min(len(doc), max_pages)
    chunks: list[str] = []
    total_chars = 0
    for i in range(pages):
        txt = doc.load_page(i).get_text("text") or ""
        chunks.append(txt)
        total_chars += len(txt)
    doc.close()
    txt_path.write_text("\n\n".join(chunks), encoding="utf-8")
    return pages, total_chars


def make_rank_text_path(rank: str) -> Path:
    rank = (rank or "").strip() or "unknown"
    return TEXT_DIR / f"__rank_{rank}__.txt"


def main() -> int:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)

    ranked = load_csv(RANKED)
    manifest = load_csv(MANIFEST) if MANIFEST.exists() else []
    manual_log = load_json_list(MANUAL_LOG)
    run_log = load_json_list(RUN_LOG)

    existing_title_norm = {title_norm(r.get("title", "")) for r in manifest}
    existing_files = {r.get("filename", "") for r in manifest}
    for p in PDF_DIR.rglob("*.pdf"):
        existing_files.add(p.name)

    candidates = []
    for row in ranked:
        if is_mdpi(row):
            continue
        tnorm = title_norm(row.get("title", ""))
        if not tnorm or tnorm in existing_title_norm:
            continue
        if row.get("filename", "") in existing_files:
            continue
        if not (row.get("pdf_url") or row.get("landing_url") or row.get("doi")):
            continue
        score, climate_hits, comm_hits = topical_score(row)
        if climate_hits == 0:
            continue
        if comm_hits == 0 and score < 90:
            continue
        candidates.append((score, climate_hits, comm_hits, row))

    candidates.sort(
        key=lambda x: (
            -x[0],
            -float(x[3].get("relevance_score") or 0.0),
            int(x[3].get("rank") or 999999),
        )
    )

    target_success = 20
    max_attempts = 260

    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept": "*/*"})

    success = 0
    attempts = 0
    selected_ranks: list[str] = []

    for _, _, _, row in candidates:
        if success >= target_success or attempts >= max_attempts:
            break

        attempts += 1
        rank = (row.get("rank") or "").strip()
        title = row.get("title") or ""

        proposed = row.get("filename") or build_filename(row)
        filename = unique_pdf_name(proposed)
        pdf_path = PDF_DIR / filename
        text_path = TEXT_DIR / f"{Path(filename).stem}.txt"

        pdf_bytes, used_url, detail = fetch_pdf(session, row)
        entry = {
            "timestamp": now_iso(),
            "rank": rank,
            "title": title,
            "filename": filename,
            "pdf_url_used": used_url,
        }

        if not pdf_bytes:
            entry["status"] = "failed_additional"
            entry["detail"] = detail
            manual_log.append(entry)
            run_log.append(entry)
            print(f"[fail] rank={rank} :: {detail}")
            continue

        try:
            pdf_path.write_bytes(pdf_bytes)
        except Exception as exc:
            entry["status"] = "failed_additional"
            entry["detail"] = f"write_error: {type(exc).__name__}: {exc}"
            manual_log.append(entry)
            run_log.append(entry)
            print(f"[fail] rank={rank} :: write_error")
            continue

        try:
            pages, chars = extract_text(pdf_path, text_path)
            entry["status"] = "downloaded_additional"
            entry["pages_extracted"] = pages
            entry["text_chars"] = chars
            entry["detail"] = "ok"
        except Exception as exc:
            rank_txt = make_rank_text_path(rank)
            rank_txt.write_text(
                "\n".join(
                    [
                        f"rank: {rank}",
                        f"title: {title}",
                        f"doi: {row.get('doi', '')}",
                        f"landing_url: {row.get('landing_url', '')}",
                        f"note: text extraction failed ({type(exc).__name__}: {exc})",
                    ]
                ),
                encoding="utf-8",
            )
            entry["status"] = "downloaded_additional_text_extract_failed"
            entry["detail"] = f"text_extract_failed: {type(exc).__name__}: {exc}"
            entry["text_fallback"] = str(rank_txt.relative_to(BASE))

        manual_log.append(entry)
        run_log.append(entry)
        success += 1
        selected_ranks.append(rank)
        print(f"[ok] rank={rank} title={title[:100]}")
        time.sleep(0.2)

    save_json(MANUAL_LOG, manual_log)
    save_json(RUN_LOG, run_log)

    print(
        json.dumps(
            {
                "target": target_success,
                "success": success,
                "attempts": attempts,
                "selected_ranks": selected_ranks,
                "remaining_needed": max(0, target_success - success),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
