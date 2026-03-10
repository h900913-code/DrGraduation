# Potential Papers

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
- PDF 파일 수: 85
- 최종 선별 편수: 85
- 직접관련: 70
- 간접관련: 15

## 실패 편수
- 최신 상태 기준 실패 건수: 59
- 대표 실패 사유: DOI 경유 403, 비-PDF 응답, 출판사 접근제한
- 재시도 성공 건수: 5
- 재시도 후 잔여 실패 건수: 12
- 최신 상태 기준 누적 복구 건수: 6

## MDPI 제외 방식
- OpenAlex 수집 단계에서 `excluded_mdpi` 상태로 제외 기록
- 도메인(`mdpi.com`) / publisher 문자열 기준 이중 확인
- 로그 기준 MDPI 제외 누적: 86건

## 파일명 규칙
- PDF: `Author ... (Year). Title. Journal.pdf`
- 노트: PDF와 동일 basename의 `.md`
- 윈도우 금지문자 제거/치환 규칙 적용

## 노트 작성 규칙
- 지정 템플릿(기본정보/배경/방법/결론/관련성/인용후보/읽기메모) 준수
- 텍스트 추출 범위 기반으로 작성하며, 불완전 읽기 여부 명시

## Hub Log Link
- Top-level hub summary is maintained in:
  - C:\Repositories\20260309_DrGraduationAdminAssist\GraduationAssistant\WORKLOG.md
- Detailed collection history remains in this folder (search_log.md, work_log_20260310.md, paper_index.md, collection_summary.md).