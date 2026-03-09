# 폴더 정리 검토 메모

마지막 업데이트: 2026-03-09

## 1. 이번 정리의 원칙

- `원본 자료`는 가능한 한 유지
- `임시 파생산출물`은 삭제
- `메인 문서`와 `보조 메모`는 분리
- `현재 효력이 약한 옛 학기 공지`는 보관 폴더로 이동

## 2. 실제로 정리한 내용

### 삭제

- 루트의 `.assistant_tmp`
- 루트의 `.assistant_tmp_qna`

사유:

- 모두 OCR 텍스트, 렌더링 PNG, crop 이미지, 임시 추출물로 구성
- 원본은 이미 `About Me(portal)`과 `QnA`에 존재
- 현재 메인 문서들에서 직접 참조하지 않음

### 이동

- [thesis_type_review.md](/C:/Repositories/20260309_DrGraduationAdminAssist/GraduationAssistant/supporting_notes/thesis_type_review.md)
  - 기존 위치: `GraduationAssistant`
  - 새 위치: `GraduationAssistant/supporting_notes`
  - 사유: [thesis_execution_plan.md](/C:/Repositories/20260309_DrGraduationAdminAssist/GraduationAssistant/thesis_execution_plan.md)의 상세 보조 메모 성격이 강해 메인 문서군과 분리

- `GSES files/archive_semester_notices`로 이동한 파일
  - `3. 2024-1학기 환경계획학과 수료요건 및 학위논문 안내(안).pdf`
  - `3. 2024-2학기 환경계획학과 수료요건 및 학위논문 안내_발표자료.pdf`
  - `5. 2024-1학기 박사논문 작성절차 안내 (1).pdf`
  - `6. 2024-1학기 박사논문 심사지원 안내 (1).pdf`
  - 사유: 현재 기준 규정이라기보다 과거 학기 공지/발표자료에 가까워 별도 보관이 더 적절

## 3. 유지 판단

### 그대로 유지한 핵심 원본 폴더

- `About Me(portal)`
- `QnA`
- `WhatIWrote`

사유:

- 모두 사용자 원본 자료
- 현재 판단과 향후 검토의 직접 근거

### 그대로 유지한 핵심 규정/서식

- `GSES files`의 현재 규정 PDF
- 논문 심사, 학위종 변경, 인정교과목, 연구윤리, 최종논문 서식 관련 파일
- `hwp/pdf` 쌍 문서

사유:

- `pdf`는 참조용
- `hwp`는 실제 편집용
- 겉보기에는 중복이지만 기능은 다름

### 그대로 유지한 메인 작업 문서

- [README.md](/C:/Repositories/20260309_DrGraduationAdminAssist/GraduationAssistant/README.md)
- [requirements_audit.md](/C:/Repositories/20260309_DrGraduationAdminAssist/GraduationAssistant/requirements_audit.md)
- [course_mapping_provisional.md](/C:/Repositories/20260309_DrGraduationAdminAssist/GraduationAssistant/course_mapping_provisional.md)
- [qna_review.md](/C:/Repositories/20260309_DrGraduationAdminAssist/GraduationAssistant/qna_review.md)
- [degree_change_reason_draft.md](/C:/Repositories/20260309_DrGraduationAdminAssist/GraduationAssistant/degree_change_reason_draft.md)
- [field_course_recognition_draft.md](/C:/Repositories/20260309_DrGraduationAdminAssist/GraduationAssistant/field_course_recognition_draft.md)
- [degree_change_submission_checklist.md](/C:/Repositories/20260309_DrGraduationAdminAssist/GraduationAssistant/degree_change_submission_checklist.md)
- [thesis_execution_plan.md](/C:/Repositories/20260309_DrGraduationAdminAssist/GraduationAssistant/thesis_execution_plan.md)
- [source_index.md](/C:/Repositories/20260309_DrGraduationAdminAssist/GraduationAssistant/source_index.md)
- [WORKLOG.md](/C:/Repositories/20260309_DrGraduationAdminAssist/GraduationAssistant/WORKLOG.md)
- [course_mapping_template.md](/C:/Repositories/20260309_DrGraduationAdminAssist/GraduationAssistant/course_mapping_template.md)

## 4. 현재 구조 해석

지금 폴더 구조는 아래처럼 읽으면 됩니다.

- 원본 개인자료: `About Me(portal)`, `QnA`, `WhatIWrote`
- dissertation 산출물: `Dissertation`
- 학교 규정/서식 원본: `GSES files`
- 내가 만든 작업 문서: `GraduationAssistant`
- 보조 메모: `GraduationAssistant/supporting_notes`
- 과거 학기 참고 공지: `GSES files/archive_semester_notices`

## 5. 추가로 일부러 하지 않은 정리

- `GSES files`의 핵심 규정/서식을 더 세분해 재배치하지 않음
  - 이유: 이미 여러 문서의 링크 근거로 사용 중이라 경로 안정성이 더 중요
- `hwp/pdf` 쌍을 하나만 남기지 않음
  - 이유: 실제 제출용 편집을 위해 둘 다 필요
- 원본 사용자 자료 이름 변경 안 함
  - 이유: 행정 추적과 출처 확인에 원래 파일명이 더 안전
