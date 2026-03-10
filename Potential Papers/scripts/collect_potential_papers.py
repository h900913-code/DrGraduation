from __future__ import annotations

import csv
import json
import re
import sys
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
import requests


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Potential Papers"
PDF_DIR = BASE / "pdf"
NOTES_DIR = BASE / "notes"
DATA_DIR = BASE / "data"
TEXT_DIR = DATA_DIR / "text"
RAW_DIR = DATA_DIR / "raw"

OPENALEX_URL = "https://api.openalex.org/works"
CROSSREF_URL = "https://api.crossref.org/works"

USER_AGENT = (
    "PotentialPapersCollector/1.0 "
    "(research workflow for local dissertation reference curation)"
)

QUERIES: list[dict[str, Any]] = [
    {"tag": "direct_yt_climate", "query": "climate change youtube", "pages": 4},
    {"tag": "direct_yt_comments", "query": "climate change youtube comments", "pages": 3},
    {"tag": "yt_misinfo", "query": "climate misinformation youtube", "pages": 3},
    {"tag": "yt_denial", "query": "climate denial youtube", "pages": 3},
    {"tag": "yt_skepticism", "query": "climate skepticism youtube", "pages": 3},
    {"tag": "yt_comm", "query": "climate communication youtube", "pages": 3},
    {"tag": "video_platform", "query": "climate communication online video platform", "pages": 3},
    {"tag": "env_comm_video", "query": "environmental communication youtube", "pages": 3},
    {"tag": "social_media_discourse", "query": "climate change social media discourse", "pages": 4},
    {"tag": "social_media_comments", "query": "climate change online comments", "pages": 4},
    {"tag": "social_media_engagement", "query": "climate change public engagement social media", "pages": 4},
    {"tag": "social_media_framing", "query": "climate change framing social media", "pages": 3},
    {"tag": "social_media_polarization", "query": "climate polarization social media", "pages": 3},
    {"tag": "social_media_misinfo", "query": "climate misinformation social media", "pages": 4},
    {"tag": "public_sphere", "query": "climate change online public sphere", "pages": 3},
    {"tag": "text_analysis", "query": "climate communication text analysis social media", "pages": 3},
    {"tag": "content_analysis", "query": "climate change content analysis youtube social media", "pages": 3},
    {"tag": "network", "query": "climate change network analysis social media discourse", "pages": 3},
    {"tag": "audience_response", "query": "climate change audience response online video", "pages": 3},
    {"tag": "korea", "query": "Korea climate communication youtube", "pages": 2},
    {"tag": "korean_social_media", "query": "Korean climate change social media discourse", "pages": 2},
]

DIRECT_TERMS = {
    "youtube",
    "you tube",
    "video platform",
    "online video",
    "comments",
    "comment",
    "video",
}
CLIMATE_TERMS = {
    "climate",
    "global warming",
    "environmental",
    "sustainability",
    "carbon neutrality",
    "carbon neutral",
}
COMM_TERMS = {
    "communication",
    "discourse",
    "frame",
    "framing",
    "engagement",
    "publics",
    "public sphere",
    "audience",
    "reception",
    "comment",
    "discussion",
}
CONTENTIOUS_TERMS = {
    "misinformation",
    "denial",
    "skeptic",
    "skepticism",
    "polarization",
    "disinformation",
    "controversy",
}
METHOD_TERMS = {
    "content analysis",
    "text analysis",
    "network",
    "computational",
    "topic model",
    "sentiment",
    "discourse analysis",
}
LOW_VALUE_TERMS = {
    "soil",
    "crop",
    "aquaculture",
    "geochemistry",
    "remote sensing",
    "machine learning model",
    "forecast",
    "temperature prediction",
    "atmospheric",
    "ocean",
    "battery",
    "photovoltaic",
    "concrete",
    "cement",
}

MDPI_HOSTS = {"mdpi.com", "www.mdpi.com"}
MDPI_PUBLISHERS = {"MDPI AG", "MDPI"}


@dataclass
class Candidate:
    openalex_id: str
    title: str
    authors: list[str]
    year: int | None
    journal: str
    doi: str
    landing_url: str
    pdf_url: str
    pdf_host: str
    publisher: str
    access_type: str
    abstract: str
    type: str
    language: str
    relevance_score: int
    relation_type: str
    matched_queries: list[str] = field(default_factory=list)
    all_pdf_urls: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
    download_status: str = ""
    download_error: str = ""
    filename: str = ""
    extracted_pages: int = 0
    text_path: str = ""


def ensure_dirs() -> None:
    for path in [BASE, PDF_DIR, NOTES_DIR, DATA_DIR, TEXT_DIR, RAW_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def log(msg: str) -> None:
    print(msg, flush=True)


def safe_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def reconstruct_abstract(inv: dict[str, list[int]] | None) -> str:
    if not inv:
        return ""
    items: list[tuple[int, str]] = []
    for word, positions in inv.items():
        for pos in positions:
            items.append((pos, word))
    return " ".join(word for _, word in sorted(items))


def nested_source(item: dict[str, Any], location_key: str = "primary_location") -> dict[str, Any]:
    location = item.get(location_key) or {}
    source = location.get("source") or {}
    return source if isinstance(source, dict) else {}


def normalize_url(url: str) -> str:
    return (url or "").strip()


def host_from_url(url: str) -> str:
    m = re.match(r"https?://([^/]+)/?", url or "")
    return m.group(1).lower() if m else ""


def is_mdpi(item: dict[str, Any], urls: list[str]) -> bool:
    hosts = {host_from_url(url) for url in urls if url}
    if hosts & MDPI_HOSTS:
        return True
    publisher = safe_text(
        nested_source(item).get("host_organization_name")
        or nested_source(item).get("display_name", "")
    )
    if publisher in MDPI_PUBLISHERS:
        return True
    locations = item.get("locations") or []
    for location in locations:
        source = location.get("source") or {}
        source_name = safe_text(source.get("host_organization_name") or source.get("display_name") or "")
        if source_name in MDPI_PUBLISHERS:
            return True
    return False


def relation_and_score(text: str, query_tag: str) -> tuple[int, str]:
    lower = text.lower()
    score = 0

    if any(term in lower for term in DIRECT_TERMS):
        score += 8
    if any(term in lower for term in CLIMATE_TERMS):
        score += 8
    if any(term in lower for term in COMM_TERMS):
        score += 6
    if any(term in lower for term in CONTENTIOUS_TERMS):
        score += 4
    if any(term in lower for term in METHOD_TERMS):
        score += 3
    if "korea" in lower or "korean" in lower or "south korea" in lower:
        score += 4

    if "youtube" in lower and "climate" in lower:
        score += 10
    if ("social media" in lower or "online" in lower) and "climate" in lower:
        score += 5
    if ("comment" in lower or "audience" in lower or "engagement" in lower) and "climate" in lower:
        score += 4

    if query_tag in {"direct_yt_climate", "direct_yt_comments", "yt_misinfo", "yt_denial", "yt_skepticism", "yt_comm"}:
        score += 3

    if any(term in lower for term in LOW_VALUE_TERMS):
        score -= 10

    relation = "indirect"
    if "youtube" in lower and "climate" in lower:
        relation = "direct"
    elif "climate" in lower and (
        "social media" in lower
        or "comment" in lower
        or "communication" in lower
        or "discourse" in lower
        or "public" in lower
    ):
        relation = "direct"
    elif "environmental communication" in lower or "climate communication" in lower:
        relation = "direct"
    return score, relation


def authors_from_item(item: dict[str, Any]) -> list[str]:
    names = []
    for author in item.get("authorships") or []:
        display = safe_text(author.get("author", {}).get("display_name") or "")
        if display:
            names.append(display)
    return names


def pick_urls(item: dict[str, Any]) -> tuple[str, str, list[str], str]:
    pdf_urls: list[str] = []
    landing_urls: list[str] = []

    best = item.get("best_oa_location") or {}
    primary = item.get("primary_location") or {}
    locations = item.get("locations") or []
    for location in [best, primary, *locations]:
        if not location:
            continue
        pdf = normalize_url(location.get("pdf_url") or "")
        landing = normalize_url(location.get("landing_page_url") or "")
        if pdf and pdf not in pdf_urls:
            pdf_urls.append(pdf)
        if landing and landing not in landing_urls:
            landing_urls.append(landing)

    pdf_url = pdf_urls[0] if pdf_urls else ""
    landing_url = landing_urls[0] if landing_urls else ""
    access_type = safe_text(best.get("version") or item.get("open_access", {}).get("oa_status") or "")
    return pdf_url, landing_url, pdf_urls, access_type


def fetch_openalex_page(session: requests.Session, query: str, page: int, per_page: int = 25) -> dict[str, Any]:
    params = {
        "search": query,
        "page": page,
        "per-page": per_page,
        "filter": "is_oa:true",
    }
    r = session.get(OPENALEX_URL, params=params, timeout=45)
    r.raise_for_status()
    return r.json()


def fetch_crossref(session: requests.Session, doi: str) -> dict[str, Any] | None:
    if not doi:
        return None
    doi = doi.replace("https://doi.org/", "").strip()
    try:
        r = session.get(f"{CROSSREF_URL}/{doi}", timeout=45)
        if r.status_code != 200:
            return None
        return r.json().get("message")
    except Exception:
        return None


def sanitize_filename_component(text: str, max_len: int = 110) -> str:
    text = safe_text(unicodedata.normalize("NFKD", text))
    text = text.replace(":", " - ")
    text = re.sub(r"[\\/*?\"<>|]", "", text)
    text = re.sub(r"\s+", " ", text).strip().strip(".")
    return text[:max_len].rstrip()


def build_filename(authors: list[str], year: int | None, title: str, journal: str) -> str:
    if not authors:
        author_part = "Unknown Author"
    elif len(authors) == 1:
        author_part = authors[0]
    elif len(authors) == 2:
        author_part = f"{authors[0]}, & {authors[1]}"
    else:
        author_part = f"{authors[0]}, et al."
    author_part = sanitize_filename_component(author_part, 80)
    year_part = str(year or "n.d.")
    title_part = sanitize_filename_component(title, 120)
    journal_part = sanitize_filename_component(journal or "Unknown Journal", 80)
    return f"{author_part} ({year_part}). {title_part}. {journal_part}"


def dedupe_candidates(items: list[Candidate]) -> list[Candidate]:
    merged: dict[str, Candidate] = {}
    for item in items:
        key = item.doi.lower() if item.doi else re.sub(r"\W+", "", item.title.lower())
        if key not in merged:
            merged[key] = item
            continue
        current = merged[key]
        current.matched_queries = sorted(set(current.matched_queries + item.matched_queries))
        current.all_pdf_urls = sorted(set(current.all_pdf_urls + item.all_pdf_urls))
        if item.relevance_score > current.relevance_score:
            item.matched_queries = current.matched_queries
            item.all_pdf_urls = current.all_pdf_urls
            merged[key] = item
    return list(merged.values())


def classify_access(source_url: str) -> str:
    host = host_from_url(source_url)
    if not source_url:
        return "unknown"
    if any(token in host for token in ["arxiv", "osf", "zenodo", "figshare", "eprints", "repository", "escholarship", "hal.science"]):
        return "repository"
    if any(token in host for token in ["springer", "nature", "tandfonline", "wiley", "sagepub", "sciencedirect", "cambridge", "oup", "frontiers", "plos", "copernicus", "asm", "biomedcentral", "acm", "ieee"]):
        return "publisher pdf"
    return "open access"


def search_candidates() -> tuple[list[Candidate], list[dict[str, Any]]]:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    raw_query_log: list[dict[str, Any]] = []
    candidates: list[Candidate] = []

    for spec in QUERIES:
        query = spec["query"]
        tag = spec["tag"]
        pages = spec["pages"]
        log(f"[search] {tag}: {query}")
        query_hits = 0
        query_kept = 0
        for page in range(1, pages + 1):
            try:
                payload = fetch_openalex_page(session, query, page=page)
            except Exception as exc:
                raw_query_log.append(
                    {
                        "tag": tag,
                        "query": query,
                        "page": page,
                        "status": "error",
                        "detail": repr(exc),
                    }
                )
                continue

            out_path = RAW_DIR / f"openalex_{tag}_page{page}.json"
            out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            results = payload.get("results") or []
            query_hits += len(results)
            raw_query_log.append(
                {
                    "tag": tag,
                    "query": query,
                    "page": page,
                    "status": "ok",
                    "hits": len(results),
                    "saved_to": str(out_path.relative_to(BASE)),
                }
            )

            for item in results:
                abstract = reconstruct_abstract(item.get("abstract_inverted_index"))
                title = safe_text(item.get("display_name") or "")
                authors = authors_from_item(item)
                journal = safe_text(nested_source(item).get("display_name", ""))
                doi = normalize_url(item.get("doi") or "")
                pdf_url, landing_url, pdf_urls, access_version = pick_urls(item)
                urls_for_mdpi = pdf_urls + ([landing_url] if landing_url else [])
                if not pdf_url:
                    continue
                if is_mdpi(item, urls_for_mdpi):
                    raw_query_log.append(
                        {
                            "tag": tag,
                            "query": query,
                            "page": page,
                            "status": "excluded_mdpi",
                            "title": title,
                            "pdf_url": pdf_url,
                        }
                    )
                    continue
                merged_text = " ".join(
                    [
                        title,
                        abstract,
                        journal,
                        " ".join(
                            concept.get("display_name", "")
                            for concept in (item.get("concepts") or [])
                        ),
                    ]
                )
                relevance_score, relation = relation_and_score(merged_text, tag)
                if relevance_score < 8:
                    continue
                query_kept += 1
                candidates.append(
                    Candidate(
                        openalex_id=item.get("id", ""),
                        title=title,
                        authors=authors,
                        year=item.get("publication_year"),
                        journal=journal,
                        doi=doi,
                        landing_url=landing_url,
                        pdf_url=pdf_url,
                        pdf_host=host_from_url(pdf_url),
                        publisher=safe_text(
                            nested_source(item).get("host_organization_name", "")
                        ),
                        access_type=access_version,
                        abstract=abstract,
                        type=safe_text(item.get("type") or ""),
                        language=safe_text(item.get("language") or ""),
                        relevance_score=relevance_score,
                        relation_type=relation,
                        matched_queries=[tag],
                        all_pdf_urls=pdf_urls,
                        raw=item,
                    )
                )
            time.sleep(0.25)
        raw_query_log.append(
            {
                "tag": tag,
                "query": query,
                "status": "summary",
                "query_hits": query_hits,
                "query_kept": query_kept,
            }
        )

    deduped = dedupe_candidates(candidates)
    deduped.sort(key=lambda c: (-c.relevance_score, c.year or 0, c.title.lower()), reverse=False)

    # Add Crossref corrections for likely final candidates.
    for candidate in deduped[:120]:
        if not candidate.doi:
            continue
        crossref = fetch_crossref(session, candidate.doi)
        if not crossref:
            continue
        if not candidate.journal:
            candidate.journal = safe_text((crossref.get("container-title") or [""])[0])
        if not candidate.year:
            issued = crossref.get("issued", {}).get("date-parts", [[None]])
            candidate.year = issued[0][0]
    return deduped, raw_query_log


def guess_alt_pdf_urls(candidate: Candidate) -> list[str]:
    urls: list[str] = []
    for url in [candidate.pdf_url, *candidate.all_pdf_urls, candidate.landing_url]:
        if url and url not in urls:
            urls.append(url)
    # Sometimes landing pages can be turned into direct PDFs.
    if candidate.landing_url and "/article/" in candidate.landing_url and not candidate.landing_url.endswith(".pdf"):
        urls.append(candidate.landing_url.rstrip("/") + "/pdf")
    return urls


def filename_for_candidate(candidate: Candidate, used: set[str]) -> str:
    base = build_filename(candidate.authors, candidate.year, candidate.title, candidate.journal)
    name = base
    counter = 2
    while f"{name}.pdf".lower() in used:
        name = f"{base} [{counter}]"
        counter += 1
    used.add(f"{name}.pdf".lower())
    return name


def validate_pdf_response(resp: requests.Response) -> bool:
    content_type = (resp.headers.get("content-type") or "").lower()
    if "pdf" in content_type:
        return True
    chunk = resp.content[:8]
    return chunk.startswith(b"%PDF")


def download_pdf(session: requests.Session, candidate: Candidate, target: Path) -> tuple[bool, str]:
    last_error = ""
    for url in guess_alt_pdf_urls(candidate):
        try:
            r = session.get(url, timeout=90, allow_redirects=True)
            if r.status_code != 200:
                last_error = f"HTTP {r.status_code} from {url}"
                continue
            if not validate_pdf_response(r):
                last_error = f"Non-PDF response from {url}"
                continue
            target.write_bytes(r.content)
            return True, url
        except Exception as exc:
            last_error = f"{url} -> {repr(exc)}"
    return False, last_error


def extract_pdf_text(pdf_path: Path, txt_path: Path, max_pages: int = 80) -> int:
    doc = fitz.open(pdf_path)
    texts = []
    pages = min(len(doc), max_pages)
    for page_num in range(pages):
        page = doc.load_page(page_num)
        texts.append(page.get_text("text"))
    doc.close()
    txt_path.write_text("\n\n".join(texts), encoding="utf-8")
    return pages


def write_candidate_csv(candidates: list[Candidate], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "rank",
                "title",
                "authors",
                "year",
                "journal",
                "doi",
                "landing_url",
                "pdf_url",
                "pdf_host",
                "publisher",
                "type",
                "language",
                "relevance_score",
                "relation_type",
                "matched_queries",
                "download_status",
                "download_error",
                "filename",
                "text_path",
            ]
        )
        for idx, c in enumerate(candidates, start=1):
            writer.writerow(
                [
                    idx,
                    c.title,
                    "; ".join(c.authors),
                    c.year or "",
                    c.journal,
                    c.doi,
                    c.landing_url,
                    c.pdf_url,
                    c.pdf_host,
                    c.publisher,
                    c.type,
                    c.language,
                    c.relevance_score,
                    c.relation_type,
                    "; ".join(c.matched_queries),
                    c.download_status,
                    c.download_error,
                    c.filename,
                    c.text_path,
                ]
            )


def main() -> int:
    ensure_dirs()
    log("[step] searching OpenAlex candidates")
    candidates, raw_query_log = search_candidates()
    raw_log_path = DATA_DIR / "openalex_query_log.json"
    raw_log_path.write_text(json.dumps(raw_query_log, ensure_ascii=False, indent=2), encoding="utf-8")

    log(f"[step] deduped candidates: {len(candidates)}")
    ranked_path = DATA_DIR / "candidate_ranked.csv"
    write_candidate_csv(candidates, ranked_path)

    selected: list[Candidate] = []
    used_names: set[str] = set()
    relation_counts = {"direct": 0, "indirect": 0}

    # Keep a mix but favor high relevance.
    for candidate in sorted(candidates, key=lambda c: (-c.relevance_score, c.year or 0, c.title.lower())):
        if candidate.relation_type == "direct" and relation_counts["direct"] < 38:
            selected.append(candidate)
            relation_counts["direct"] += 1
        elif candidate.relation_type == "indirect" and relation_counts["indirect"] < 20:
            selected.append(candidate)
            relation_counts["indirect"] += 1
        if len(selected) >= 70:
            break

    log(f"[step] selected for download attempts: {len(selected)}")
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    success_count = 0
    failure_count = 0
    for candidate in selected:
        base_name = filename_for_candidate(candidate, used_names)
        candidate.filename = f"{base_name}.pdf"
        pdf_path = PDF_DIR / candidate.filename
        txt_path = TEXT_DIR / f"{base_name}.txt"
        ok, detail = download_pdf(session, candidate, pdf_path)
        if ok:
            candidate.download_status = "downloaded"
            candidate.download_error = ""
            try:
                candidate.extracted_pages = extract_pdf_text(pdf_path, txt_path)
                candidate.text_path = str(txt_path.relative_to(BASE))
            except Exception as exc:
                candidate.download_status = "downloaded_text_extract_failed"
                candidate.download_error = repr(exc)
            success_count += 1
        else:
            candidate.download_status = "failed"
            candidate.download_error = detail
            failure_count += 1
        time.sleep(0.2)

    final_candidates = [c for c in selected if c.download_status.startswith("downloaded")]
    final_candidates.sort(key=lambda c: (-c.relevance_score, c.year or 0, c.title.lower()))

    downloaded_path = DATA_DIR / "downloaded_candidates.csv"
    write_candidate_csv(selected, downloaded_path)
    final_json = DATA_DIR / "final_candidates.json"
    final_json.write_text(
        json.dumps([c.__dict__ for c in final_candidates], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    log(f"[done] downloaded={success_count} failed={failure_count}")
    log(f"[done] saved ranked list -> {ranked_path}")
    log(f"[done] saved downloaded list -> {downloaded_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
