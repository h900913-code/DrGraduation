from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

import fitz
import requests


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Potential Papers"
REGION_BASE = BASE / "by_region"
PDF_DIR = REGION_BASE / "pdf_region"
DATA_DIR = BASE / "data"
TEXT_DIR = DATA_DIR / "text"
RANKED_PATH = DATA_DIR / "candidate_ranked.csv"
USER_AGENT = "PotentialPapersCollector/1.0 (manual second-pass downloader)"


def log(msg: str) -> None:
    print(msg, flush=True)


def load_rows() -> list[dict[str, str]]:
    with RANKED_PATH.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def extract_text(pdf_path: Path, txt_path: Path, max_pages: int = 80) -> int:
    doc = fitz.open(pdf_path)
    pages = min(len(doc), max_pages)
    text = []
    for i in range(pages):
        text.append(doc.load_page(i).get_text("text"))
    doc.close()
    txt_path.write_text("\n\n".join(text), encoding="utf-8")
    return pages


def validate_pdf(resp: requests.Response) -> bool:
    if "pdf" in (resp.headers.get("content-type") or "").lower():
        return True
    return resp.content[:8].startswith(b"%PDF")


def filename_to_txt(filename: str) -> Path:
    return TEXT_DIR / f"{Path(filename).stem}.txt"


def safe(text: str, limit: int = 100) -> str:
    text = (text or "").replace(":", " - ")
    for ch in '\\/*?"<>|':
        text = text.replace(ch, "")
    text = " ".join(text.split()).strip().strip(".")
    return text[:limit].rstrip()


def build_filename(row: dict[str, str]) -> str:
    authors = [part.strip() for part in (row.get("authors") or "").split(";") if part.strip()]
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
    return f"{safe(author_part, 80)} ({year}). {safe(title, 120)}. {safe(journal, 80)}.pdf"


def main(argv: list[str]) -> int:
    ranks = {str(int(arg)) for arg in argv[1:]}
    if not ranks:
        print("usage: python download_selected_from_ranked.py <rank> [<rank> ...]")
        return 2

    rows = load_rows()
    target_rows = [row for row in rows if row["rank"] in ranks]
    if not target_rows:
        print("no matching ranks")
        return 1

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)

    log_path = DATA_DIR / "manual_download_log.json"
    existing = []
    if log_path.exists():
        existing = json.loads(log_path.read_text(encoding="utf-8"))

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    for row in target_rows:
        filename = row["filename"] or build_filename(row)
        pdf_path = PDF_DIR / filename
        txt_path = filename_to_txt(filename)

        if pdf_path.exists():
            status = {
                "rank": row["rank"],
                "title": row["title"],
                "status": "already_exists",
                "filename": filename,
            }
            existing.append(status)
            log(f"[skip] {row['rank']} {row['title']}")
            continue

        urls = []
        for key in ["pdf_url", "landing_url"]:
            val = (row.get(key) or "").strip()
            if val and val not in urls:
                urls.append(val)
        if row.get("landing_url") and "/article/" in row["landing_url"] and row["landing_url"] + "/pdf" not in urls:
            urls.append(row["landing_url"].rstrip("/") + "/pdf")

        ok = False
        detail = ""
        used_url = ""
        for url in urls:
            try:
                resp = session.get(url, timeout=90, allow_redirects=True)
                if resp.status_code != 200:
                    detail = f"HTTP {resp.status_code} from {url}"
                    continue
                if not validate_pdf(resp):
                    detail = f"Non-PDF response from {url}"
                    continue
                pdf_path.write_bytes(resp.content)
                used_url = url
                ok = True
                break
            except Exception as exc:
                detail = f"{url} -> {repr(exc)}"
        if ok:
            try:
                pages = extract_text(pdf_path, txt_path)
                status = {
                    "rank": row["rank"],
                    "title": row["title"],
                    "status": "downloaded",
                    "url": used_url,
                    "filename": filename,
                    "pages_extracted": pages,
                }
            except Exception as exc:
                status = {
                    "rank": row["rank"],
                    "title": row["title"],
                    "status": "downloaded_text_extract_failed",
                    "url": used_url,
                    "filename": filename,
                    "detail": repr(exc),
                }
            log(f"[ok] {row['rank']} {row['title']}")
        else:
            status = {
                "rank": row["rank"],
                "title": row["title"],
                "status": "failed",
                "detail": detail,
                "filename": filename,
            }
            log(f"[fail] {row['rank']} {row['title']} :: {detail}")
        existing.append(status)
        time.sleep(0.2)

    log_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
