# Reference Audit Handoff

작성일: 2026-03-10

## 1. 작업 범위
- 검토 대상 문서
  - `WhatIWrote/Doctoral_Research_Plan_5p_KOR.docx`
  - `WhatIWrote/Doctoral_Research_Plan_5p_ENG.docx`
  - `WhatIWrote/Doctoral_Research_Plan_Full_KOR.docx`
- 작업 목적
  - 본문 인용과 참고문헌의 매핑을 만들고
  - 각 인용이 실제로 해당 문장/문단의 주장 유형을 얼마나 지지하는지 엄격하게 점검
  - 누락 인용, 미사용 참고문헌, 문서 간 불일치도 함께 식별

## 2. 생성 완료 파일
- `WhatIWrote/reference_audit.csv`
- `WhatIWrote/reference_audit_summary.md`

## 3. 점검 결과 요약
- 총 점검 행 수: 39
- 실제 본문 인용 사례: 35
- 목록에는 있으나 본문에서 호출되지 않은 참고문헌: 4
- 본문 인용인데 참고문헌 목록에 없는 항목: 1

지지 적합성 판정
- 직접 지지: 15
- 부분 지지: 13
- 간접 지지: 6
- 부적합: 0
- 확인 불충분: 1

## 4. 가장 중요한 발견
### 4.1 즉시 수정이 필요한 구조적 문제
- `Doctoral_Research_Plan_5p_KOR.docx`의 `4.4 행위자 네트워크 분석` 문단에서 `Newman, 2010`이 본문에 인용되지만 참고문헌 목록에 없음.
- `Doctoral_Research_Plan_5p_ENG.docx`의 대응 문단은 `centrality measures`와 `community-detection techniques`를 함께 언급하면서 `Traag et al., 2019`만 인용하고 있음.

### 4.2 과부하된 인용
- 두 5페이지 문서의 서론에서 `Allgaier, 2019`, `Shapiro & Park, 2018`, `Lim/임연수 외, 2021`만으로
  - 한국 범위
  - 영상-댓글-행위자 결집의 통합성
  - actor clustering
  - 플랫폼 적합성
  을 한꺼번에 지지하려고 하고 있음.
- 이 조합은 배경 설명으로는 쓸 수 있으나, 현재 문장 강도 기준으로는 직접 지지보다 `부분 지지` 또는 `간접 지지`에 가까움.

### 4.3 Full_KOR에서의 주의점
- `de Nadal, 2024`는 유튜브의 기후 허위정보 연구로는 적합하지만, 한국 유튜브 장기 통합 분석의 공백을 직접 입증하는 문헌은 아님.
- `Mohammad et al., 2016`는 stance detection 방법론 일반에는 유용하지만, 기후 유튜브 댓글의 정서/태도 분석을 직접 받치기에는 약함.
- `boyd & Crawford, 2012`는 연구윤리 일반의 보조 근거로는 가능하나, 실제 인터넷 연구 윤리 절차의 직접 근거는 `Franzke et al., 2020` 쪽이 더 적합함.

## 5. 목록에는 있으나 본문에서 안 쓰인 참고문헌
- `Doctoral_Research_Plan_5p_KOR.docx`
  - `임연수. (2023). 기후변화 관련 유튜브 콘텐츠에 대한 토픽모델링...`
- `Doctoral_Research_Plan_5p_ENG.docx`
  - `Lim, Y. (2023). Topic modeling of YouTube contents on climate change...`
- `Doctoral_Research_Plan_Full_KOR.docx`
  - `IPCC. (2023). Climate change 2023: Synthesis report.`
  - `United Nations Framework Convention on Climate Change. (2015). Paris Agreement.`

## 6. 본문에는 있으나 참고문헌에 없는 항목
- `Doctoral_Research_Plan_5p_KOR.docx`
  - `Newman, 2010`

## 7. 원문 확인 상태
저장소 안에서 직접 원문 또는 원문급 파일을 확인한 문헌
- `Allgaier, 2019`
- `de Nadal, 2024`
- `Franzke et al., 2020`

원문이 저장소에 없어 서지/초록/외부 정보 기준으로만 판단한 문헌
- `Beck, 1992`
- `Hilgartner & Bosk, 1988`
- `Blei et al., 2003`
- `Pang & Lee, 2008`
- `Shapiro & Park, 2018`
- `Traag et al., 2019`
- `Douglas & Wildavsky, 1982`
- `Grootendorst, 2022`
- `Mohammad et al., 2016`
- `Newman, 2010`
- `boyd & Crawford, 2012`
- `IPCC, 2023`
- `UNFCCC, 2015`
- `임연수 2021/2023`

## 8. 다음에 해야 할 일
우선순위 순서

1. `Doctoral_Research_Plan_5p_KOR.docx`
   - `Newman, 2010` 참고문헌을 추가할지
   - 아니면 본문에서 `centrality` 관련 표현을 줄일지 결정

2. `Doctoral_Research_Plan_5p_ENG.docx`
   - `4.4 Actor Network Analysis`에 `Newman`류 일반 네트워크 문헌을 추가하거나
   - 문장을 `community detection` 중심으로 축소

3. 두 5페이지 문서의 서론 문단 정리
   - `한국 유튜브가 적합한 공간`이라는 진술을 유지하되
   - `actor clustering`과 `통합적 분석 가능성`을 조금 완화하거나
   - 댓글/네트워크 관련 추가 문헌을 넣어 문장 강도와 근거를 맞출 것

4. `Doctoral_Research_Plan_Full_KOR.docx`
   - `de Nadal, 2024`와 `Allgaier, 2019`가 맡는 역할을 분리
   - `국외 유튜브 사례`와 `국내 선행연구 공백`을 한 문장에 묶지 않도록 조정

5. `정서/태도 분석` 근거 보강
   - 가능하면 기후 담론 또는 댓글 자료 기반의 stance/attitude 문헌을 추가 검토

6. 미사용 참고문헌 처리
   - `Lim 2023`, `IPCC 2023`, `UNFCCC 2015`를 실제 본문에 쓸지
   - 아니면 목록에서 제거할지 결정

## 9. 다음 세션 시작용 추천 질문
다음에 돌아와서 바로 이어가려면 아래처럼 물으면 된다.

- `내가 오늘은 뭐 해야해`
- `reference audit 결과 기준으로 어떤 문장부터 고치면 돼`
- `5p_KOR의 Newman 누락부터 고쳐줘`
- `5p_ENG 4.4 인용을 적절하게 다시 맞춰줘`
- `부분 지지/간접 지지 사례만 추려서 수정안 제안해줘`

## 10. 참고
- 세부 판정 근거는 `WhatIWrote/reference_audit.csv`에 행 단위로 들어 있음.
- 사람이 먼저 읽기 쉬운 요약은 `WhatIWrote/reference_audit_summary.md`에 있음.
