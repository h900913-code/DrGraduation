from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Potential Papers"
DATA = BASE / "data"
REGION_BASE = BASE / "by_region"
PDF_DIR = REGION_BASE / "pdf_region"

RANKED = DATA / "candidate_ranked.csv"
FINAL = DATA / "final_candidates.json"
MANUAL = DATA / "manual_download_log.json"
OUT_LOG = DATA / "retry_download_log.json"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def norm(s: str) -> str:
    return re.sub(r"\W+", "", (s or "").lower())


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def is_pdf_bytes(content: bytes) -> bool:
    return content[:5] == b"%PDF-"


def extract_pdf_links(html: str, base_url: str) -> list[str]:
    links = set()
    for m in re.finditer(r"href=[\"']([^\"']+)[\"']", html, flags=re.I):
        href = m.group(1)
        if ".pdf" in href.lower() or "download" in href.lower():
            links.add(requests.compat.urljoin(base_url, href))
    return list(links)


def doi_suffix(doi_url: str) -> str:
    m = re.search(r"10\.[^/]+/.+", doi_url or "", flags=re.I)
    return m.group(0) if m else ""


def variant_urls(row: dict[str, str], final: dict[str, object] | None) -> list[str]:
    urls = []

    def add(u: str | None):
        if not u:
            return
        u = u.strip()
        if not u:
            return
        if u not in urls:
            urls.append(u)

    add(row.get("pdf_url"))
    add(row.get("landing_url"))
    add(row.get("doi"))

    if final:
        for u in (final.get("all_pdf_urls") or []):
            add(u)
        raw = final.get("raw") or {}
        oa = raw.get("open_access") or {}
        add(oa.get("oa_url"))
        for loc in (raw.get("locations") or []):
            add((loc or {}).get("pdf_url"))
            add((loc or {}).get("landing_page_url"))

    doi = doi_suffix(row.get("doi", "") or row.get("landing_url", ""))
    if doi:
        add(f"https://doi.org/{doi}")
        add(f"https://dx.doi.org/{doi}")
        add(f"https://api.crossref.org/works/{doi}")

        if doi.startswith("10.1002/"):
            add(f"https://onlinelibrary.wiley.com/doi/pdfdirect/{doi}")
            add(f"https://onlinelibrary.wiley.com/doi/pdf/{doi}")
        if doi.startswith("10.1080/"):
            add(f"https://www.tandfonline.com/doi/pdf/{doi}?needAccess=true")
        if doi.startswith("10.1177/"):
            add(f"https://journals.sagepub.com/doi/pdf/{doi}")
        if doi.startswith("10.3389/"):
            part = doi.split("/", 1)[1]
            add(f"https://www.frontiersin.org/articles/{part}/pdf")
        if doi.startswith("10.17645/"):
            add((row.get("pdf_url") or "").replace("/article/view/", "/article/download/"))

    # landing 변형
    landing = row.get("landing_url", "")
    if landing:
        add(landing.rstrip("/") + "/pdf")
        if "tandfonline.com/doi/" in landing:
            add(landing.replace("/doi/full/", "/doi/pdf/") + "?needAccess=true")
            add(landing.replace("/doi/abs/", "/doi/pdf/") + "?needAccess=true")
        if "journals.sagepub.com/doi/" in landing:
            add(landing.replace("/doi/full/", "/doi/pdf/"))
            add(landing.replace("/doi/abs/", "/doi/pdf/"))

    return urls


def fetch_pdf(session: requests.Session, url: str) -> tuple[bool, bytes, str]:
    try:
        r = session.get(url, timeout=60, allow_redirects=True)
    except Exception as e:
        return False, b"", f"request_error:{e!r}"

    ctype = (r.headers.get("content-type") or "").lower()
    if r.status_code != 200:
        return False, b"", f"http_{r.status_code}"

    if "application/pdf" in ctype or is_pdf_bytes(r.content):
        return True, r.content, "ok"

    # html이면 링크 추출해서 2차 시도
    text = r.text[:400000]
    links = extract_pdf_links(text, r.url)
    for link in links[:30]:
        try:
            r2 = session.get(link, timeout=60, allow_redirects=True)
            ctype2 = (r2.headers.get("content-type") or "").lower()
            if r2.status_code == 200 and ("application/pdf" in ctype2 or is_pdf_bytes(r2.content)):
                return True, r2.content, f"html_follow:{link}"
        except Exception:
            pass

    return False, b"", "non_pdf"


def main() -> int:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    ranked = load_csv(RANKED)
    by_rank = {r.get("rank", ""): r for r in ranked}

    finals = json.loads(FINAL.read_text(encoding="utf-8")) if FINAL.exists() else []
    by_title = {norm(x.get("title", "")): x for x in finals}
    by_doi = {norm(x.get("doi", "")): x for x in finals if x.get("doi")}

    manual = json.loads(MANUAL.read_text(encoding="utf-8")) if MANUAL.exists() else []
    failed = [x for x in manual if str(x.get("status", "")).startswith("failed")]

    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept": "*/*"})

    retry_logs = []
    downloaded = 0

    def safe_filename(name: str, rank: str) -> str:
        bad = '\\/:*?"<>|'
        for ch in bad:
            name = name.replace(ch, "")
        name = " ".join(name.split())
        if not name.lower().endswith(".pdf"):
            name += ".pdf"
        if len(name) <= 180:
            return name
        stem = Path(name).stem[:140].rstrip()
        h = hashlib.sha1(name.encode("utf-8", errors="ignore")).hexdigest()[:8]
        return f"{stem} [{rank}-{h}].pdf"

    def write_pdf_with_fallback(content: bytes, preferred_name: str, rank: str) -> tuple[Path, str]:
        preferred = PDF_DIR / preferred_name
        try:
            preferred.write_bytes(content)
            return preferred, preferred_name
        except Exception:
            alt_name = safe_filename(preferred_name, rank)
            alt = PDF_DIR / alt_name
            alt.write_bytes(content)
            return alt, alt_name

    for item in failed:
        rank = str(item.get("rank", ""))
        row = by_rank.get(rank)
        if not row:
            retry_logs.append({"rank": rank, "title": item.get("title"), "status": "skip_no_rank"})
            continue

        filename = row.get("filename") or item.get("filename")
        if not filename:
            retry_logs.append({"rank": rank, "title": item.get("title"), "status": "skip_no_filename"})
            continue

        out_pdf = PDF_DIR / filename
        if out_pdf.exists():
            retry_logs.append({"rank": rank, "title": row.get("title"), "status": "already_exists"})
            continue

        fmeta = by_title.get(norm(row.get("title", ""))) or by_doi.get(norm(row.get("doi", "")))
        urls = variant_urls(row, fmeta)

        success = False
        detail = ""
        used = ""

        for url in urls[:80]:
            ok, content, reason = fetch_pdf(session, url)
            if ok:
                try:
                    out_pdf, final_name = write_pdf_with_fallback(content, filename, rank)
                    filename = final_name
                    success = True
                    used = url
                    detail = reason
                    break
                except Exception as e:
                    detail = f"{url}::write_error:{e!r}"
            else:
                detail = f"{url}::{reason}"
            time.sleep(0.15)

        if success:
            downloaded += 1
            retry_logs.append({
                "rank": rank,
                "title": row.get("title"),
                "status": "downloaded_retry",
                "url": used,
                "detail": detail,
                "filename": filename,
                "size": out_pdf.stat().st_size,
            })
            # manual log append
            manual.append({
                "rank": rank,
                "title": row.get("title"),
                "status": "downloaded_retry",
                "url": used,
                "filename": filename,
                "detail": detail,
            })
            print(f"[ok] {rank} {row.get('title')}")
        else:
            retry_logs.append({
                "rank": rank,
                "title": row.get("title"),
                "status": "failed_retry",
                "detail": detail,
                "filename": filename,
            })
            print(f"[fail] {rank} {row.get('title')} :: {detail}")

    OUT_LOG.write_text(json.dumps(retry_logs, ensure_ascii=False, indent=2), encoding="utf-8")
    MANUAL.write_text(json.dumps(manual, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"retry_total={len(failed)} downloaded_retry={downloaded}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
