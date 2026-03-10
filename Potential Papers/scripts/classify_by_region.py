from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import shutil
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "Potential Papers"
MANIFEST = BASE / "data" / "papers_manifest.csv"
CACHE_PATH = BASE / "data" / "openalex_country_cache.json"

OUT_BASE = BASE / "by_region"
OUT_PDF = OUT_BASE / "pdf_region"
OUT_NOTES = OUT_BASE / "notes"
PDF_DIR = OUT_PDF
NOTES_DIR = OUT_NOTES
LEGACY_PDF_DIR = BASE / "pdf"
LEGACY_NOTES_DIR = BASE / "notes"
OUT_INDEX = OUT_BASE / "region_index.csv"
OUT_SUMMARY = OUT_BASE / "README.md"

UA = "PotentialPapersRegionClassifier/1.0"


def doi_norm(s: str) -> str:
    s = (s or "").strip().lower()
    m = re.search(r"10\.[^\s/]+/.+", s)
    return m.group(0).rstrip(".").strip() if m else ""


def safe_part(s: str) -> str:
    s = (s or "Unknown").strip()
    for ch in '\\/:*?"<>|':
        s = s.replace(ch, "-")
    s = " ".join(s.split())
    return s or "Unknown"


def safe_filename(name: str, rank: str) -> str:
    out = safe_part(name)
    if len(out) <= 150:
        return out
    h = hashlib.sha1(out.encode("utf-8", errors="ignore")).hexdigest()[:8]
    stem = Path(out).stem[:110].rstrip()
    ext = Path(out).suffix or ".pdf"
    return f"{stem} [{rank}-{h}]{ext}"


def norm_title(s: str) -> str:
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\W+", "", s.lower())


def load_manifest() -> list[dict[str, str]]:
    with MANIFEST.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def same_path(a: Path, b: Path) -> bool:
    try:
        return a.resolve() == b.resolve()
    except Exception:
        return str(a).lower() == str(b).lower()


def find_pdf_path(row: dict[str, str]) -> Path | None:
    raw_rel = (row.get("pdf_path") or "").strip()
    if raw_rel:
        candidate = BASE / raw_rel.replace("\\", "/")
        if candidate.exists():
            return candidate

    fname = Path((row.get("filename") or "").strip()).name
    if fname:
        for candidate in [
            PDF_DIR / fname,
            LEGACY_PDF_DIR / fname,
        ]:
            if candidate.exists():
                return candidate
    return (BASE / raw_rel.replace("\\", "/")) if raw_rel else None


def find_note_path(pdf_path: Path | None, row: dict[str, str]) -> Path | None:
    candidates: list[Path] = []
    if pdf_path and pdf_path.exists():
        candidates.append(NOTES_DIR / f"{pdf_path.stem}.md")
        try:
            rel = pdf_path.relative_to(PDF_DIR)
            candidates.append(NOTES_DIR / rel.parent / f"{pdf_path.stem}.md")
        except Exception:
            pass
    fname = Path((row.get("filename") or "").strip()).stem
    if fname:
        candidates.append(NOTES_DIR / f"{fname}.md")
        candidates.append(LEGACY_NOTES_DIR / f"{fname}.md")
    for p in candidates:
        if p.exists():
            return p
    return None


def get_country_from_openalex(doi: str, session: requests.Session, cache: dict) -> tuple[str | None, str]:
    if not doi:
        return None, "no_doi"
    if doi in cache:
        return cache[doi].get("country_code"), cache[doi].get("method", "cache")

    url = f"https://api.openalex.org/works/https://doi.org/{doi}"
    cc = None
    method = "openalex_none"
    try:
        r = session.get(url, timeout=40)
        if r.status_code == 200:
            d = r.json()
            auth = d.get("authorships") or []
            for a in auth:
                for inst in (a.get("institutions") or []):
                    code = inst.get("country_code")
                    if code:
                        cc = code
                        method = "openalex_first_author_inst"
                        break
                if cc:
                    break
            if not cc:
                countries = d.get("countries") or []
                if countries:
                    cc = countries[0]
                    method = "openalex_countries"
        else:
            method = f"openalex_http_{r.status_code}"
    except Exception as e:
        method = f"openalex_error:{type(e).__name__}"

    cache[doi] = {"country_code": cc, "method": method}
    return cc, method


def infer_country_fallback(row: dict[str, str]) -> tuple[str, str]:
    title = (row.get("title") or "").lower()
    host = (row.get("pdf_host") or "").lower()
    landing = (row.get("landing_url") or "").lower()

    keyword_rules = [
        ("pakistan", "PK"),
        ("weibo", "CN"),
        ("u.s.", "US"),
        ("united states", "US"),
        ("korea", "KR"),
        ("africa", "ZA"),
        ("dutch", "NL"),
        ("spain", "ES"),
    ]
    for kw, code in keyword_rules:
        if kw in title:
            return code, f"fallback_title:{kw}"

    domain_rules = [
        (".uk", "GB"),
        (".es", "ES"),
        (".de", "DE"),
        (".fr", "FR"),
        (".it", "IT"),
        (".cn", "CN"),
        (".jp", "JP"),
        (".kr", "KR"),
        (".au", "AU"),
        (".ca", "CA"),
        (".se", "SE"),
        (".fi", "FI"),
        (".nl", "NL"),
    ]
    blob = host + " " + landing
    for suf, code in domain_rules:
        if suf in blob:
            return code, f"fallback_domain:{suf}"

    return "UNK", "fallback_unknown"


COUNTRY_NAME = {
    "US": "United States",
    "GB": "United Kingdom",
    "UK": "United Kingdom",
    "CA": "Canada",
    "AU": "Australia",
    "DE": "Germany",
    "FR": "France",
    "IT": "Italy",
    "ES": "Spain",
    "NL": "Netherlands",
    "SE": "Sweden",
    "FI": "Finland",
    "DK": "Denmark",
    "NO": "Norway",
    "CH": "Switzerland",
    "AT": "Austria",
    "BE": "Belgium",
    "IE": "Ireland",
    "PT": "Portugal",
    "GR": "Greece",
    "TR": "Turkey",
    "CY": "Cyprus",
    "RS": "Serbia",
    "UA": "Ukraine",
    "RU": "Russia",
    "PL": "Poland",
    "CZ": "Czech Republic",
    "HU": "Hungary",
    "RO": "Romania",
    "BG": "Bulgaria",
    "HR": "Croatia",
    "SI": "Slovenia",
    "EE": "Estonia",
    "LV": "Latvia",
    "LT": "Lithuania",
    "IS": "Iceland",
    "LU": "Luxembourg",
    "MT": "Malta",
    "CN": "China",
    "JP": "Japan",
    "KR": "South Korea",
    "IN": "India",
    "PK": "Pakistan",
    "BD": "Bangladesh",
    "ID": "Indonesia",
    "MY": "Malaysia",
    "SG": "Singapore",
    "TH": "Thailand",
    "VN": "Vietnam",
    "PH": "Philippines",
    "TW": "Taiwan",
    "HK": "Hong Kong",
    "IR": "Iran",
    "IL": "Israel",
    "AE": "United Arab Emirates",
    "SA": "Saudi Arabia",
    "ZA": "South Africa",
    "NG": "Nigeria",
    "KE": "Kenya",
    "EG": "Egypt",
    "MA": "Morocco",
    "BR": "Brazil",
    "AR": "Argentina",
    "CL": "Chile",
    "CO": "Colombia",
    "MX": "Mexico",
    "PE": "Peru",
    "NZ": "New Zealand",
    "UNK": "Unknown",
}

CONTINENT = {
    "US": "North America",
    "CA": "North America",
    "MX": "North America",
    "BR": "South America",
    "AR": "South America",
    "CL": "South America",
    "CO": "South America",
    "PE": "South America",
    "GB": "Europe",
    "UK": "Europe",
    "DE": "Europe",
    "FR": "Europe",
    "IT": "Europe",
    "ES": "Europe",
    "NL": "Europe",
    "SE": "Europe",
    "FI": "Europe",
    "DK": "Europe",
    "NO": "Europe",
    "CH": "Europe",
    "AT": "Europe",
    "BE": "Europe",
    "IE": "Europe",
    "PT": "Europe",
    "GR": "Europe",
    "TR": "Europe/Asia",
    "CY": "Europe/Asia",
    "RS": "Europe",
    "UA": "Europe",
    "RU": "Europe/Asia",
    "PL": "Europe",
    "CZ": "Europe",
    "HU": "Europe",
    "RO": "Europe",
    "BG": "Europe",
    "HR": "Europe",
    "SI": "Europe",
    "EE": "Europe",
    "LV": "Europe",
    "LT": "Europe",
    "IS": "Europe",
    "LU": "Europe",
    "MT": "Europe",
    "CN": "Asia",
    "JP": "Asia",
    "KR": "Asia",
    "IN": "Asia",
    "PK": "Asia",
    "BD": "Asia",
    "ID": "Asia",
    "MY": "Asia",
    "SG": "Asia",
    "TH": "Asia",
    "VN": "Asia",
    "PH": "Asia",
    "TW": "Asia",
    "HK": "Asia",
    "IR": "Asia",
    "IL": "Asia",
    "AE": "Asia",
    "SA": "Asia",
    "ZA": "Africa",
    "NG": "Africa",
    "KE": "Africa",
    "EG": "Africa",
    "MA": "Africa",
    "AU": "Oceania",
    "NZ": "Oceania",
    "UNK": "Unknown",
}


def main() -> int:
    rows = load_manifest()
    cache = load_cache()

    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept": "application/json"})

    OUT_PDF.mkdir(parents=True, exist_ok=True)
    OUT_NOTES.mkdir(parents=True, exist_ok=True)

    out_rows = []

    for r in rows:
        pdf_path = find_pdf_path(r)
        note_path = find_note_path(pdf_path, r)

        doi = doi_norm(r.get("doi", "") or r.get("landing_url", ""))
        cc, method = get_country_from_openalex(doi, session, cache)
        if not cc:
            cc, method = infer_country_fallback(r)

        cc = (cc or "UNK").upper()
        country = COUNTRY_NAME.get(cc, cc)
        continent = CONTINENT.get(cc, "Unknown")

        continent_dir = safe_part(continent)
        country_dir = safe_part(country)

        tgt_pdf_dir = OUT_PDF / continent_dir / country_dir
        tgt_note_dir = OUT_NOTES / continent_dir / country_dir
        tgt_pdf_dir.mkdir(parents=True, exist_ok=True)
        tgt_note_dir.mkdir(parents=True, exist_ok=True)

        copied_pdf_name = ""
        copied_note_name = ""

        if pdf_path and pdf_path.exists():
            copied_pdf_name = pdf_path.name
            pdf_target = tgt_pdf_dir / pdf_path.name
            try:
                if not same_path(pdf_path, pdf_target):
                    shutil.copy2(pdf_path, pdf_target)
            except Exception:
                copied_pdf_name = safe_filename(pdf_path.name, r.get("rank", "x"))
                pdf_target = tgt_pdf_dir / copied_pdf_name
                if not same_path(pdf_path, pdf_target):
                    shutil.copy2(pdf_path, pdf_target)

        if note_path and note_path.exists():
            copied_note_name = note_path.name
            note_target = tgt_note_dir / note_path.name
            try:
                if not same_path(note_path, note_target):
                    shutil.copy2(note_path, note_target)
            except Exception:
                copied_note_name = safe_filename(note_path.name, r.get("rank", "x"))
                note_target = tgt_note_dir / copied_note_name
                if not same_path(note_path, note_target):
                    shutil.copy2(note_path, note_target)

        out_rows.append(
            {
                "rank": r.get("rank", ""),
                "title": r.get("title", ""),
                "filename": pdf_path.name if pdf_path else Path(r.get("filename", "")).name,
                "country_code": cc,
                "country": country,
                "continent": continent,
                "classification_method": method,
                "pdf_copied": "yes" if (pdf_path and pdf_path.exists()) else "no",
                "note_copied": "yes" if (note_path and note_path.exists()) else "no",
                "copied_pdf_name": copied_pdf_name if (pdf_path and pdf_path.exists()) else "",
                "copied_note_name": copied_note_name if (note_path and note_path.exists()) else "",
            }
        )

    save_cache(cache)

    with OUT_INDEX.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "rank",
                "title",
                "filename",
                "country_code",
                "country",
                "continent",
                "classification_method",
                "pdf_copied",
                "note_copied",
                "copied_pdf_name",
                "copied_note_name",
            ],
        )
        w.writeheader()
        w.writerows(out_rows)

    # summary
    by_cont = {}
    by_country = {}
    unknown = 0
    for x in out_rows:
        c = x["continent"]
        k = x["country"]
        by_cont[c] = by_cont.get(c, 0) + 1
        by_country[k] = by_country.get(k, 0) + 1
        if x["country_code"] == "UNK":
            unknown += 1

    lines = [
        "# Region Classification",
        "",
        "- 기준: DOI 기반 OpenAlex 저자 소속 국가(가능한 경우), 실패 시 제목/도메인 규칙 보완",
        f"- 총 분류 대상: {len(out_rows)}",
        f"- Unknown 분류: {unknown}",
        "",
        "## Continent Counts",
    ]
    for k, v in sorted(by_cont.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"- {k}: {v}")

    lines.append("")
    lines.append("## Top Country Counts")
    for k, v in sorted(by_country.items(), key=lambda kv: (-kv[1], kv[0]))[:20]:
        lines.append(f"- {k}: {v}")

    OUT_SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"classified={len(out_rows)} unknown={unknown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
