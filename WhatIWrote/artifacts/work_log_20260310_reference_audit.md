# Work Log: Reference Audit

날짜: 2026-03-10

## 오늘 한 일
- 박사논문/연구계획서 3개 문서의 본문 인용과 참고문헌을 전수 점검했다.
- 각 문서의 참고문헌 목록을 추출했다.
- 본문 인용 사례를 문단 단위로 분리했다.
- 같은 참고문헌이 여러 문단에서 반복되면 별도 사례로 기록했다.
- 저장소 안에 원문 PDF/MD/TXT가 있는지 검색했다.
- 원문이 없는 항목은 서지정보와 외부 확인 가능한 자료를 기준으로 보수적으로 판정했다.
- 결과를 CSV와 MD 요약으로 저장했다.

## 사용한 주요 입력 파일
- `WhatIWrote/docx/Doctoral_Research_Plan_5p_KOR.docx`
- `WhatIWrote/docx/Doctoral_Research_Plan_5p_ENG.docx`
- `WhatIWrote/docx/Doctoral_Research_Plan_Full_KOR.docx`
- `WhatIWrote/20260210 계획서(연구재단제출).pdf`
- `WhatIWrote/20260304 계획서(지도교수 면담).pdf`
- `WhatIWrote/docx/Description of intended doctoral research_JH.Park.docx`

## 생성한 결과 파일
- `WhatIWrote/artifacts/reference_audit.csv`
- `WhatIWrote/artifacts/reference_audit_summary.md`
- `WhatIWrote/artifacts/reference_audit_handoff_20260310.md`
- `WhatIWrote/artifacts/work_log_20260310_reference_audit.md`

## 핵심 결과
- 총 점검 사례: 35
- 직접 지지: 15
- 부분 지지: 13
- 간접 지지: 6
- 부적합: 0
- 확인 불충분: 1

추가 이상
- 본문 인용인데 참고문헌 누락: 1
- 참고문헌 목록에는 있으나 본문 미사용: 4

## 가장 중요한 이슈
1. `Doctoral_Research_Plan_5p_KOR.docx`
   - `Newman, 2010` 본문 인용은 있는데 참고문헌 없음

2. `Doctoral_Research_Plan_5p_ENG.docx`
   - `4.4 Actor Network Analysis`에서 `Traag et al., 2019`만으로 `centrality + community detection`를 동시에 받치고 있음

3. 두 5페이지 문서 서론
   - `Allgaier / Shapiro & Park / Lim 2021` 조합에 너무 많은 역할이 실려 있음

4. `Doctoral_Research_Plan_Full_KOR.docx`
   - `de Nadal, 2024`와 `Allgaier, 2019`가 한국 사례 공백 설명까지 동시에 떠맡고 있음

5. `정서/태도 분석` 방법론
   - `Pang & Lee, 2008`만으로는 태도·지연 정당화 범주까지 직접 지지하기 부족함

## 다음에 해야 할 일
우선순위

1. `5p_KOR`의 `Newman, 2010` 누락 처리
2. `5p_ENG` 4.4 인용 구조 정리
3. 두 5페이지 문서 서론 문장 강도와 근거 맞추기
4. `Full_KOR`에서 국외 사례 문헌과 국내 연구 공백 문장을 분리
5. stance/attitude 관련 보강 문헌 검토
6. 미사용 참고문헌 정리 여부 결정

## 다음에 나한테 물어보면 좋은 말
- `내가 오늘은 뭐 해야해`
- `reference audit 다음 작업 우선순위 알려줘`
- `지금 가장 먼저 고쳐야 할 인용 3개만 말해줘`
- `5p_KOR의 Newman 문제부터 해결하자`
- `부분 지지 사례만 추려서 수정안 써줘`

## 메모
- 지금 단계에서는 문서 본문을 수정하지 않았다.
- 이번 작업은 감사표 작성과 우선 수정 포인트 정리에 집중했다.
- 실제 DOCX 수정은 다음 세션에서 `reference_audit.csv`를 기준으로 진행하면 된다.

## Follow-up Note

- The 2026-03-11 follow-up session is logged in `WhatIWrote/artifacts/work_log_20260311_reference_followup.md`.
- Use `WhatIWrote/artifacts/reference_audit_summary.md` for the current status snapshot.
- Use `WhatIWrote/artifacts/reference_audit_handoff_20260310.md` for the remaining follow-up items.
