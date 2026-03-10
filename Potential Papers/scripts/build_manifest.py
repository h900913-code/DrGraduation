from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Potential Papers"
PDF_DIR = BASE / "by_region" / "pdf_region"
TEXT_DIR = BASE / "data" / "text"
RANKED = BASE / "data" / "candidate_ranked.csv"
DOWNLOADED = BASE / "data" / "downloaded_candidates.csv"
MANUAL_LOG = BASE / "data" / "manual_download_log.json"
OUT = BASE / "data" / "papers_manifest.csv"


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    ranked_rows = load_csv(RANKED)
    ranked_by_rank = {row["rank"]: row for row in ranked_rows}
    ranked_by_title = {row["title"]: row for row in ranked_rows}

    rows: dict[str, dict[str, str]] = {}

    for row in load_csv(DOWNLOADED):
        if not row.get("download_status", "").startswith("downloaded"):
            continue
        if not row.get("filename"):
            continue
        rows[row["filename"]] = row

    if MANUAL_LOG.exists():
        logs = json.loads(MANUAL_LOG.read_text(encoding="utf-8"))
        for item in logs:
            if not str(item.get("status", "")).startswith("downloaded"):
                continue
            rank = str(item.get("rank", ""))
            meta = ranked_by_rank.get(rank, {})
            title = item.get("title", "")
            if not meta and title:
                meta = ranked_by_title.get(title, {})
            if not meta:
                continue
            filename = item["filename"]
            row = dict(meta)
            row["filename"] = filename
            row["download_status"] = item["status"]
            row["text_path"] = str((TEXT_DIR / f"{Path(filename).stem}.txt").relative_to(BASE))
            rows[filename] = row

    ordered = []
    for pdf_path in sorted(PDF_DIR.rglob("*.pdf")):
        row = rows.get(pdf_path.name)
        if not row:
            continue
        text_path = TEXT_DIR / f"{pdf_path.stem}.txt"
        rank_alt = TEXT_DIR / f"__rank_{row.get('rank', '').strip()}__.txt"
        file_hash = hashlib.sha1(pdf_path.name.encode("utf-8", errors="ignore")).hexdigest()[:12]
        file_alt = TEXT_DIR / f"__file_{file_hash}.txt"
        chosen_text = text_path if text_path.exists() else (
            rank_alt if rank_alt.exists() else (
                file_alt if file_alt.exists() else None
            )
        )
        row["pdf_path"] = str(pdf_path.relative_to(BASE))
        row["text_path"] = str(chosen_text.relative_to(BASE)) if chosen_text else ""
        row["pdf_exists"] = "yes"
        row["text_exists"] = "yes" if chosen_text else "no"
        ordered.append(row)

    fieldnames = [
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
        "pdf_path",
        "text_path",
        "pdf_exists",
        "text_exists",
    ]
    with OUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in ordered:
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    print(f"manifest_rows={len(ordered)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
