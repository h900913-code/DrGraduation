from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Potential Papers"
DATA = BASE / "data"
REGION_BASE = BASE / "by_region"
PDF_DIR = REGION_BASE / "pdf_region"
RANKED = DATA / "candidate_ranked.csv"
MANUAL = DATA / "manual_download_log.json"
OUT = DATA / "retry_crossref_log.json"

UA = "Mozilla/5.0"

custom = {
    "64": [
        "https://www.cogitatiopress.com/mediaandcommunication/article/download/253/253",
    ],
    "57": [
        "https://journals.sagepub.com/doi/pdf/10.1177/1075547020942228",
    ],
    "58": [
        "https://journals.sagepub.com/doi/pdf/10.1177/0963662520981729",
    ],
    "155": [
        "https://journals.sagepub.com/doi/pdf/10.1177/20563051231168370",
    ],
    "114": [
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC9433270/pdf/",
        "https://downloads.hindawi.com/journals/jeph/2022/6294436.pdf",
    ],
    "143": [
        "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/gch2.201600008",
    ],
    "194": [
        "https://www.researchgate.net/publication/381197746_Exploring_Climate_Change_Discourse_on_Social_Media_and_Blogs_Using_a_Topic_Modeling_Analysis",
    ],
}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def is_pdf(content: bytes, ctype: str) -> bool:
    return "application/pdf" in (ctype or "").lower() or content[:5] == b"%PDF-"


def safe_filename(name: str, rank: str) -> str:
    for ch in '\\/:*?"<>|':
        name = name.replace(ch, "")
    name = " ".join(name.split())
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    if len(name) <= 180:
        return name
    h = hashlib.sha1(name.encode("utf-8", errors="ignore")).hexdigest()[:8]
    return f"{Path(name).stem[:140].rstrip()} [{rank}-{h}].pdf"


def crossref_pdf_links(doi_url: str, session: requests.Session) -> list[str]:
    m = re.search(r"10\.[^/]+/.+", doi_url or "")
    if not m:
        return []
    doi = m.group(0)
    api = f"https://api.crossref.org/works/{doi}"
    out = []
    try:
        r = session.get(api, timeout=45)
        if r.status_code != 200:
            return out
        msg = r.json().get("message", {})
        for lk in msg.get("link", []) or []:
            u = (lk or {}).get("URL")
            c = (lk or {}).get("content-type", "")
            if u and ("pdf" in (c or "").lower() or u.lower().endswith(".pdf")):
                out.append(u)
        # fallback resource primary URL
        ru = msg.get("resource", {}).get("primary", {}).get("URL")
        if ru:
            out.append(ru)
    except Exception:
        pass
    # unique preserve order
    seen = set()
    uniq = []
    for u in out:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def main() -> int:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    ranked = load_csv(RANKED)
    by_rank = {r.get("rank", ""): r for r in ranked}

    manual = json.loads(MANUAL.read_text(encoding="utf-8")) if MANUAL.exists() else []
    latest = {}
    for x in manual:
        rk = str(x.get("rank", "")).strip()
        if rk:
            latest[rk] = x
    targets = [x for x in latest.values() if str(x.get("status", "")).startswith("failed")]

    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept": "*/*"})

    logs = []
    ok_count = 0

    for item in targets:
        rk = str(item.get("rank", "")).strip()
        row = by_rank.get(rk)
        if not row:
            logs.append({"rank": rk, "status": "skip_no_row"})
            continue

        fname = item.get("filename") or row.get("filename") or f"rank_{rk}.pdf"
        out = PDF_DIR / fname
        if out.exists():
            logs.append({"rank": rk, "status": "already_exists"})
            continue

        urls = []
        for u in [row.get("pdf_url"), row.get("landing_url"), row.get("doi")]:
            if u and u not in urls:
                urls.append(u)
        for u in custom.get(rk, []):
            if u not in urls:
                urls.append(u)
        for u in crossref_pdf_links(row.get("doi", "") or row.get("landing_url", ""), session):
            if u not in urls:
                urls.append(u)

        success = False
        detail = ""
        used = ""

        for u in urls[:30]:
            try:
                r = session.get(u, timeout=60, allow_redirects=True)
                if r.status_code == 200 and is_pdf(r.content, r.headers.get("content-type", "")):
                    try:
                        out.write_bytes(r.content)
                        final_name = fname
                    except Exception:
                        final_name = safe_filename(fname, rk)
                        out = PDF_DIR / final_name
                        out.write_bytes(r.content)
                    success = True
                    used = u
                    detail = "ok"
                    fname = final_name
                    break
                detail = f"{u}::http_{r.status_code}::{r.headers.get('content-type','')}"
            except Exception as e:
                detail = f"{u}::err::{e!r}"

        if success:
            ok_count += 1
            logs.append({"rank": rk, "status": "downloaded_crossref_retry", "url": used, "filename": fname, "size": out.stat().st_size})
            manual.append({"rank": rk, "title": row.get("title", ""), "status": "downloaded_crossref_retry", "url": used, "filename": fname})
            print(f"[ok] {rk} {row.get('title')}")
        else:
            logs.append({"rank": rk, "status": "failed_crossref_retry", "detail": detail, "filename": fname})
            print(f"[fail] {rk} {row.get('title')} :: {detail}")

    OUT.write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding="utf-8")
    MANUAL.write_text(json.dumps(manual, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"targets={len(targets)} ok={ok_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
