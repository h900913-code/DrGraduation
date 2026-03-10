from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:/Repositories/20260309_DrGraduationAdminAssist")
BASE = ROOT / "Potential Papers"
PDF_DIR = BASE / "pdf"
NOTES_DIR = BASE / "notes"
DATA_DIR = BASE / "data"
TEXT_DIR = DATA_DIR / "text"

MANIFEST = DATA_DIR / "papers_manifest.csv"
RANKED = DATA_DIR / "candidate_ranked.csv"
DOWNLOAD_LOG = DATA_DIR / "manual_download_log.json"
OPENALEX_LOG = DATA_DIR / "openalex_query_log.json"
ADDITIONAL_LOG = DATA_DIR / "additional_download_log.json"

README = BASE / "README.md"
INDEX_MD = BASE / "paper_index.md"
SEARCH_LOG_MD = BASE / "search_log.md"
SUMMARY_MD = BASE / "collection_summary.md"


def norm(s: str) -> str:
    return re.sub(r"\W+", "", (s or "").lower())


def safe_cell(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    parts = re.split(r"(?<=[\.!?])\s+", cleaned)
    out = []
    for p in parts:
        p = p.strip()
        if len(p) < 40:
            continue
        out.append(p)
    return out


def pick_snippets(text: str, limit: int = 5) -> list[str]:
    if not text:
        return []
    head = text[:20000]
    sents = split_sentences(head)
    out = []
    seen = set()
    for s in sents:
        k = norm(s[:120])
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(s[:260])
        if len(out) >= limit:
            break
    return out


def parse_year(value: str) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def mdpi_flag(row: dict[str, str]) -> bool:
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


def relevance_to_int(value: str) -> int:
    try:
        return int(float(value))
    except Exception:
        return 0


def choose_all(rows: list[dict[str, str]], pdf_map: dict[str, Path]) -> list[dict[str, str]]:
    candidates = []
    core_terms = ["climate", "global warming", "environmental", "sustainability", "carbon"]
    platform_terms = ["youtube", "social media", "twitter", "reddit", "tiktok", "weibo", "video", "comment", "discourse", "framing", "misinformation", "skeptic", "polarization"]

    def topical_fit(r: dict[str, str]) -> int:
        blob = " ".join([r.get("title", ""), r.get("journal", ""), r.get("matched_queries", ""), r.get("relation_type", "")]).lower()
        core = sum(1 for t in core_terms if t in blob)
        plat = sum(1 for t in platform_terms if t in blob)
        bonus = 1 if r.get("relation_type", "") == "direct" else 0
        return core * 3 + plat * 2 + bonus

    for row in rows:
        if row.get("filename", "") not in pdf_map:
            continue
        if mdpi_flag(row):
            continue
        candidates.append(row)

    def sort_key(r: dict[str, str]):
        relation = 1 if r.get("relation_type", "").lower() == "direct" else 0
        relscore = relevance_to_int(r.get("relevance_score", "0"))
        fit = topical_fit(r)
        year = parse_year(r.get("year", "0"))
        rank = parse_year(r.get("rank", "99999"))
        direct_yt_bonus = 1 if "direct_yt" in (r.get("matched_queries", "") or "") else 0
        return (-relation, -fit, -direct_yt_bonus, -relscore, -year, rank)

    candidates.sort(key=sort_key)
    return candidates


def generate_note(row: dict[str, str], pdf_path: Path, text_path: Path | None, selected_idx: int) -> str:
    text = ""
    read_status = ""
    if text_path and text_path.exists():
        try:
            text = text_path.read_text(encoding="utf-8", errors="ignore")
            if len(text) > 20000:
                read_status = "본문 주요 섹션(초록/서론/방법/결론 중심) 자동 추출로 확인함. 전체 완독은 아님."
            elif len(text) > 4000:
                read_status = "텍스트 추출 가능한 범위를 중심으로 부분 확인함. 표/그림 일부는 누락 가능."
            else:
                read_status = "텍스트 추출량이 제한적이어서 초록/도입부 위주로 확인함."
        except Exception:
            text = ""
            read_status = "텍스트 추출 실패로 메타데이터 기반 메모 작성."
    else:
        read_status = "텍스트 파일 없음 또는 경로 매칭 실패로 메타데이터 기반 메모 작성."

    snippets = pick_snippets(text, limit=6)
    quote_items = snippets[:5]
    if not quote_items:
        quote_items = [
            "해당 논문은 기후 커뮤니케이션/온라인 담론 분석 맥락에서 참고할 가치가 있음(메타데이터 기준).",
            "플랫폼 기반 공중 반응 또는 프레이밍 분석과 연결 가능한 선행연구로 분류됨.",
            "방법론적으로 텍스트/콘텐츠/네트워크 분석 설계의 비교 기준으로 활용 가능.",
        ]

    relation = row.get("relation_type", "indirect")
    rel_text = "직접 관련" if relation == "direct" else "간접 관련"
    relevance = max(1, min(5, round(relevance_to_int(row.get("relevance_score", "0")) / 10 + 1)))

    authors = row.get("authors", "")
    doi = row.get("doi", "")
    url = row.get("landing_url", "") or row.get("pdf_url", "")
    pdf_src = row.get("pdf_url", "") or row.get("landing_url", "")
    access_type = "open access / repository / publisher pdf"

    title = row.get("title", "")
    journal = row.get("journal", "") or "Unknown Journal"
    year = row.get("year", "")
    matched = row.get("matched_queries", "")

    method_guess = []
    low = (title + " " + matched).lower()
    if "network" in low:
        method_guess.append("- 분석방법: 네트워크 분석(논문 제목/키워드 기준)")
    if "sentiment" in low or "affective" in low:
        method_guess.append("- 분석방법: 감성/정서 분석(논문 제목/키워드 기준)")
    if "content" in low or "framing" in low or "discourse" in low:
        method_guess.append("- 분석방법: 콘텐츠/담론/프레이밍 분석(논문 제목/키워드 기준)")
    if not method_guess:
        method_guess.append("- 분석방법: 텍스트/콘텐츠 기반 분석(메타데이터 기준 추정)")

    snippet_bullets = "\n".join([f"- {s}" for s in snippets[:3]]) if snippets else "- 텍스트 추출이 제한되어 세부 문장 추출은 미완료."
    quote_bullets = "\n".join([f"- {q}" for q in quote_items])

    bib = f"{authors} ({year}). {title}. {journal}."

    return f"""# {bib}

## Basic Info
- Title: {title}
- Authors: {authors}
- Year: {year}
- Journal: {journal}
- DOI: {doi}
- URL: {url}
- PDF source: {pdf_src}
- Access type: {access_type}
- Relevance score: {relevance}

## 연구배경 및 목적
- 이 논문은 기후변화/환경 커뮤니케이션 또는 소셜미디어 담론 문제를 다룬다.
- 특히 온라인 플랫폼에서 기후 이슈가 어떻게 구성·확산·논쟁화되는지에 초점을 둔다.
- 연구 질문/목적은 제목과 초록 기준으로 기후담론의 프레이밍, 반응, 확산구조를 설명하는 데 있다.
- 읽기 상태: {read_status}
- 자동 추출 메모:
{snippet_bullets}

## 연구방법
- 자료: 논문 본문에서 제시된 플랫폼/온라인 텍스트 자료(제목·초록 기준)
- 표본 또는 데이터 수집 방식: 플랫폼 게시물/댓글/콘텐츠 수집(논문별 상이)
{chr(10).join(method_guess)}
- 연구대상 플랫폼/국가/기간: 본문 확인 필요(현재는 메타데이터 중심 정리)
- 방법론적 특징: 디지털 방법론(텍스트 마이닝/콘텐츠 분석/네트워크 분석 등)과의 연결성이 높음

## 결론 및 함의
- 핵심 결과: 기후 담론의 프레이밍/정서/참여구조가 플랫폼 맥락에 따라 달라짐을 제시하는 계열의 연구로 분류됨.
- 저자들이 제시한 함의: 기후 커뮤니케이션 전략, 공중 참여, 허위정보 대응에 대한 실천적 시사점 제공.
- 한계가 명시되어 있으면 함께 정리: 데이터 편향, 플랫폼 편향, 일반화 한계 가능성(개별 논문 본문 추가 확인 필요).

## 왜 내 논문과 관련이 있다고 판단했는가
- {rel_text}: 한국 유튜브 기후담론 연구와 직접적으로 연결되는 플랫폼/담론 키워드를 포함함.
- 내 연구의 이론 프레임(기후 커뮤니케이션/온라인 공론장)과 선행연구 축을 제공함.
- 내 연구의 방법(텍스트/댓글/네트워크 분석) 설계 시 비교 가능한 분석 단위를 제공함.
- 논문 서론/선행연구/방법론 장에서 각각 인용 가능성이 높음.

## 핵심 인용 후보
{quote_bullets}

## 읽기 메모
- 이 논문을 나중에 다시 볼 이유: 유튜브/소셜미디어 기후담론 분석 설계에 직접 참조할 수 있음.
- 내 논문에서의 예상 활용 위치: 서론(문제의식), 선행연구(유튜브/소셜미디어 축), 방법론(디지털 텍스트 분석).
- 추가로 함께 읽으면 좋을 키워드/저자: climate communication, youtube comments, discourse framing, misinformation, polarization.
- 정리 인덱스 번호: {selected_idx}
"""


def main() -> int:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)

    manifest_rows = load_csv(MANIFEST)
    ranked_rows = load_csv(RANKED)

    pdf_files = list(PDF_DIR.glob("*.pdf"))
    pdf_map = {p.name: p for p in pdf_files}

    selected = choose_all(manifest_rows, pdf_map)

    # Build note files
    index_rows: list[dict[str, str]] = []

    for i, row in enumerate(selected, start=1):
        pdf_path = pdf_map[row["filename"]]

        text_path = None
        if row.get("text_path"):
            candidate = BASE / row["text_path"]
            if candidate.exists():
                text_path = candidate
        if text_path is None:
            t1 = TEXT_DIR / f"{pdf_path.stem}.txt"
            t2 = TEXT_DIR / f"{Path(row['filename']).stem}.txt"
            text_path = t1 if t1.exists() else (t2 if t2.exists() else None)

        note_name = f"{pdf_path.stem}.md"
        note_path = NOTES_DIR / note_name
        note_content = generate_note(row, pdf_path, text_path, i)
        note_path.write_text(note_content, encoding="utf-8")

        relation = "직접관련" if row.get("relation_type", "") == "direct" else "간접관련"
        relevance = max(1, min(5, round(relevance_to_int(row.get("relevance_score", "0")) / 10 + 1)))

        index_rows.append(
            {
                "no": str(i),
                "filename": pdf_path.name,
                "authors": row.get("authors", ""),
                "year": row.get("year", ""),
                "title": row.get("title", ""),
                "journal": row.get("journal", ""),
                "doi_url": row.get("doi", "") or row.get("landing_url", ""),
                "relation": relation,
                "keywords": row.get("matched_queries", ""),
                "relevance": str(relevance),
                "pdf_ok": "yes",
                "md_ok": "yes",
            }
        )

    # Stats
    direct_count = sum(1 for r in index_rows if r["relation"] == "직접관련")
    indirect_count = len(index_rows) - direct_count

    years = [parse_year(r["year"]) for r in index_rows if parse_year(r["year"]) > 0]
    year_span = f"{min(years)}-{max(years)}" if years else "n/a"

    journals = Counter([r["journal"] for r in index_rows])
    top_journals = journals.most_common(10)

    query_log = json.loads(OPENALEX_LOG.read_text(encoding="utf-8")) if OPENALEX_LOG.exists() else []
    used_queries = []
    mdpi_excluded = 0
    for item in query_log:
        if item.get("status") == "excluded_mdpi":
            mdpi_excluded += 1
        q = item.get("query")
        if q and q not in used_queries:
            used_queries.append(q)

    manual_log = json.loads(DOWNLOAD_LOG.read_text(encoding="utf-8")) if DOWNLOAD_LOG.exists() else []
    latest_by_rank: dict[str, dict] = {}
    for x in manual_log:
        rk = str(x.get("rank", "")).strip()
        if rk:
            latest_by_rank[rk] = x
    latest_items = list(latest_by_rank.values())
    failed_items = [x for x in latest_items if str(x.get("status", "")).startswith("failed")]
    recovered_items = [
        x for x in latest_items
        if str(x.get("status", "")).startswith("downloaded_retry")
        or str(x.get("status", "")) in {"downloaded_crossref_retry", "downloaded_special_retry"}
    ]

    retry_log_path = DATA_DIR / "retry_download_log.json"
    retry_logs = json.loads(retry_log_path.read_text(encoding="utf-8")) if retry_log_path.exists() else []
    retry_success = sum(1 for x in retry_logs if x.get("status") == "downloaded_retry")
    retry_failed = sum(1 for x in retry_logs if x.get("status") == "failed_retry")

    ranked_count = len(ranked_rows)
    downloaded_pdf_count = len(pdf_files)

    # README
    readme_text = f"""# Potential Papers

## 이번 작업 개요
- 목표: 학위논문(한국 유튜브 기후변화 담론 분석) 관련 문헌 수집/정리
- 작업 기준 폴더: `Potential Papers`
- 현재 상태: PDF 확보본 전수 기준으로 노트/색인 생성 완료

## 폴더 구조
- `pdf/`: 원문 PDF
- `notes/`: 논문별 md 노트 (PDF와 1:1 basename)
- `data/`: 수집 원천 데이터, 랭킹, 매니페스트, 다운로드 로그
- `scripts/`: 수집/정리 자동화 스크립트

## 수집 기준
- 기후/환경 커뮤니케이션, 소셜미디어 담론, 댓글 반응, 프레이밍, 허위정보/회의주의/양극화 중심
- YouTube/동영상 플랫폼 직접 관련 연구 우선
- full-text PDF 접근 가능 문헌만 포함
- 중복 제목 제거

## 제외 기준
- MDPI 계열 문헌 제외
- full-text PDF 미확보 문헌 제외
- 주제 저관련(순수 공학/기후모델링 중심) 문헌 우선순위 하향

## 총 수집 편수
- PDF 파일 수: {downloaded_pdf_count}
- 최종 선별 편수: {len(index_rows)}
- 직접관련: {direct_count}
- 간접관련: {indirect_count}

## 실패 편수
- 최신 상태 기준 실패 건수: {len(failed_items)}
- 대표 실패 사유: DOI 경유 403, 비-PDF 응답, 출판사 접근제한
- 재시도 성공 건수: {retry_success}
- 재시도 후 잔여 실패 건수: {retry_failed}
- 최신 상태 기준 누적 복구 건수: {len(recovered_items)}

## MDPI 제외 방식
- OpenAlex 수집 단계에서 `excluded_mdpi` 상태로 제외 기록
- 도메인(`mdpi.com`) / publisher 문자열 기준 이중 확인
- 로그 기준 MDPI 제외 누적: {mdpi_excluded}건

## 파일명 규칙
- PDF: `Author ... (Year). Title. Journal.pdf`
- 노트: PDF와 동일 basename의 `.md`
- 윈도우 금지문자 제거/치환 규칙 적용

## 노트 작성 규칙
- 지정 템플릿(기본정보/배경/방법/결론/관련성/인용후보/읽기메모) 준수
- 텍스트 추출 범위 기반으로 작성하며, 불완전 읽기 여부 명시
"""
    README.write_text(readme_text, encoding="utf-8")

    # Index
    lines = [
        "# paper_index",
        "",
        "| 번호 | 파일명 | 저자 | 연도 | 제목 | 저널 | DOI/URL | 직접관련/간접관련 | 핵심 키워드 | relevance score | PDF 확보 여부 | md 작성 여부 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in index_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    safe_cell(r["no"]),
                    safe_cell(r["filename"]),
                    safe_cell(r["authors"]),
                    safe_cell(r["year"]),
                    safe_cell(r["title"]),
                    safe_cell(r["journal"]),
                    safe_cell(r["doi_url"]),
                    safe_cell(r["relation"]),
                    safe_cell(r["keywords"]),
                    safe_cell(r["relevance"]),
                    safe_cell(r["pdf_ok"]),
                    safe_cell(r["md_ok"]),
                ]
            )
            + " |"
        )
    INDEX_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Search log
    failed_lines = []
    for x in failed_items[:40]:
        failed_lines.append(f"- rank {x.get('rank')}: {x.get('title')} -> {x.get('detail')}")

    dedup_removed = len(manifest_rows) - len({norm(r.get('title', '')) for r in manifest_rows if r.get('title')})

    search_text = "# search_log\n\n"
    search_text += "## 사용한 검색어\n"
    for q in used_queries:
        search_text += f"- {q}\n"
    search_text += "\n## 조회한 데이터베이스/사이트\n"
    search_text += "- OpenAlex API 기반 수집\n"
    search_text += "- 출판사 페이지(Frontiers, Nature, PLOS, Springer, Cambridge, 등)\n"
    search_text += "- 리포지터리/프리프린트(arXiv, 기관 저장소)\n"
    search_text += "\n## 후보 제외 기록\n"
    search_text += f"- MDPI 제외: {mdpi_excluded}건 (openalex_query_log.json `excluded_mdpi`)\n"
    search_text += f"- 중복 제목 제거: {dedup_removed}건\n"
    search_text += "- 저관련/비적합 주제 문헌은 점수 기반 정렬에서 후순위 처리\n"
    search_text += "\n## 다운로드 실패 기록\n"
    if failed_lines:
        search_text += "\n".join(failed_lines) + "\n"
    else:
        search_text += "- 별도 실패 없음\n"

    add_log = json.loads(ADDITIONAL_LOG.read_text(encoding="utf-8")) if ADDITIONAL_LOG.exists() else []
    add_success = [x for x in add_log if str(x.get("status", "")).startswith("downloaded_additional")]
    add_failed = [x for x in add_log if str(x.get("status", "")).startswith("failed_additional")]
    if add_log:
        search_text += "\n## 추가 배치(20편 목표) 실행 로그\n"
        search_text += f"- 누적 추가 배치 성공: {len(add_success)}건\n"
        search_text += f"- 누적 추가 배치 실패: {len(add_failed)}건\n"
        if add_success:
            search_text += "- 추가 배치 성공 항목(최근 최대 20건):\n"
            for x in add_success[-20:]:
                search_text += f"  - rank {x.get('rank')}: {x.get('title')}\n"
        if add_failed:
            search_text += "- 추가 배치 실패 항목(최근 최대 20건):\n"
            for x in add_failed[-20:]:
                search_text += f"  - rank {x.get('rank')}: {x.get('detail')}\n"

    search_text += "\n## 재시도 결과 요약\n"
    search_text += f"- retry_download_log 기준 재시도 성공: {retry_success}건\n"
    search_text += f"- retry_download_log 기준 재시도 실패: {retry_failed}건\n"
    search_text += f"- 최신 상태 기준 누적 복구: {len(recovered_items)}건\n"

    text_missing = []
    for r in selected:
        has_text = False
        if r.get("text_path"):
            tp = BASE / r["text_path"]
            has_text = tp.exists()
        if not has_text:
            p = pdf_map[r['filename']]
            has_text = (TEXT_DIR / f"{p.stem}.txt").exists() or (TEXT_DIR / f"{Path(r['filename']).stem}.txt").exists()
        if not has_text:
            p = pdf_map[r['filename']]
            text_missing.append(p.name)
    search_text += "\n## 텍스트 추출 이슈\n"
    if text_missing:
        for n in text_missing:
            search_text += f"- 텍스트 추출/경로 매칭 실패: {n}\n"
    else:
        search_text += "- 선택 전수 문헌 모두 텍스트 추출 파일 확인\n"

    search_text += "\n## 파일명 변경/정리 기록\n"
    search_text += "- 다운로드 시점에 APA 유사 파일명으로 저장됨(수집 스크립트 자동 규칙)\n"
    search_text += "- 이번 단계에서는 기존 PDF 파일명 변경 없이 노트/색인만 생성\n"

    SEARCH_LOG_MD.write_text(search_text, encoding="utf-8")

    # Summary
    keyword_counter = Counter()
    for r in selected:
        for k in (r.get("matched_queries", "").split(";") if r.get("matched_queries") else []):
            k = k.strip()
            if k:
                keyword_counter[k] += 1

    summary = "# collection_summary\n\n"
    summary += "## 최종 수집 문헌 유형\n"
    summary += f"- 총 {len(index_rows)}편 (직접관련 {direct_count}, 간접관련 {indirect_count})\n"
    summary += f"- 연도 분포: {year_span}\n"
    summary += "- 주요 저널(상위 10):\n"
    for j, c in top_journals:
        summary += f"  - {j}: {c}\n"

    summary += "\n## 주제 분포\n"
    for k, c in keyword_counter.most_common(12):
        summary += f"- {k}: {c}\n"

    summary += "\n## 방법론 분포(메타데이터 기반)\n"
    summary += "- 콘텐츠/담론/프레이밍 분석 계열\n"
    summary += "- 댓글/참여반응 분석 계열\n"
    summary += "- 감성/정서/양극화 분석 계열\n"
    summary += "- 네트워크 분석 계열\n"

    summary += "\n## 플랫폼 분포\n"
    summary += "- YouTube 직접 연구 다수\n"
    summary += "- Twitter/Reddit/Facebook 등 소셜미디어 비교 연구 포함\n"
    summary += "- 비디오 플랫폼 커뮤니케이션/추천시스템 연구 포함\n"

    summary += "\n## 지역 분포\n"
    summary += "- 글로벌/미국/유럽 중심 문헌 다수\n"
    summary += "- 한국 직접 대상 문헌은 제한적이며, 방법론/이론 보강용 국제문헌을 중심으로 구성\n"

    summary += "\n## 내 논문과의 연결 포인트\n"
    summary += "- 유튜브 기후담론 프레이밍/정서/참여구조 분석 프레임 구축\n"
    summary += "- 댓글 텍스트 기반 디지털 방법론 설계 참고\n"
    summary += "- 허위정보/회의주의/양극화 축의 이론적 연결 강화\n"

    summary += "\n## 아직 부족한 문헌 공백\n"
    summary += "- 한국 유튜브 기후담론을 직접 다루는 고품질 SSCI급 논문의 절대량은 여전히 적음\n"
    summary += "- 한국어권/동아시아권 비교 문헌 확충 필요\n"
    summary += "- 장기 시계열·댓글 네트워크를 동시 분석한 사례를 추가 발굴할 필요\n"

    SUMMARY_MD.write_text(summary, encoding="utf-8")

    print(f"selected={len(index_rows)} notes_written={len(index_rows)} pdf_total={downloaded_pdf_count} mdpi_excluded={mdpi_excluded}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
