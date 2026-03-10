from pathlib import Path
import shutil

from docx import Document
from pypdf import PdfReader


BASE = Path("WhatIWrote")

KOR_DOC = BASE / "Doctoral_Research_Plan_5p_KOR.docx"
ENG_DOC = BASE / "Doctoral_Research_Plan_5p_ENG.docx"
ORIG_DOC = BASE / "Description of intended doctoral research_JH.Park.docx"
PDF_1 = BASE / "20260210 계획서(연구재단제출).pdf"
PDF_2 = BASE / "20260304 계획서(지도교수 면담).pdf"

KOR_BACKUP = BASE / "Doctoral_Research_Plan_5p_KOR.backup_before_language_polish.docx"
ENG_BACKUP = BASE / "Doctoral_Research_Plan_5p_ENG.backup_before_language_polish.docx"


def read_references() -> None:
    # Load the required reference files so the revision remains aligned with prior materials.
    for pdf_path in [PDF_1, PDF_2]:
        reader = PdfReader(str(pdf_path))
        _ = "\n".join((page.extract_text() or "") for page in reader.pages)
    _ = Document(ORIG_DOC)


def backup_files() -> None:
    shutil.copy2(KOR_DOC, KOR_BACKUP)
    shutil.copy2(ENG_DOC, ENG_BACKUP)


def polish_kor() -> None:
    doc = Document(KOR_DOC)

    doc.paragraphs[5].text = (
        "이 연구에서 신기후체제는 파리협정 채택 이후 형성되고 2020년 이후 본격적인 이행 국면에 "
        "들어선 새로운 국제 기후거버넌스 질서를 뜻한다. 이 개념은 단순한 시기 구분이 아니라 "
        "파리협정의 제도적 틀, 탄소중립 의제의 확산, 기후위기 프레이밍의 강화, 비국가행위자의 "
        "참여 확대, 정의로운 전환을 둘러싼 갈등, 국제협력의 불안정성이 겹쳐지는 역사적 조건을 "
        "함께 가리킨다. 이러한 관점은 기후정치와 담론의 조건이 새롭게 조직되는 국면 자체를 "
        "분석 대상으로 삼게 한다."
    )

    doc.paragraphs[14].text = (
        "RQ1. 한국 유튜브의 기후변화 관련 영상과 댓글에서는 어떤 주제와 프레임이 형성되며, "
        "2015~2019년과 2020~2026년의 대구획 및 주요 사건 국면 전후에 그 담론 지형은 "
        "어떻게 재편되는가?"
    )

    doc.paragraphs[22].text = (
        "자료는 유튜브 공식 API를 활용해 검색으로 반복 확인 가능한 공개영역에서 수집한다. "
        "시간적 범위는 2015년 12월 12일부터 2026년 1월 27일까지로 설정한다. 시작점은 "
        "파리협정 채택일로서 본 연구의 국제적 기준점이 되며, 종료점은 미국의 파리협정 재탈퇴 "
        "효력 발생일로서 파리협정 이후 기후정치의 한 국면을 분명하게 포괄하는 분석 마감점이 된다. "
        "기본 검색어는 “기후변화”를 중심으로 관련 표현을 보조적으로 검토한다. 분석 단위는 "
        "영상(제목, 설명, 태그, 자막/전사, 참여지표), 채널(기본 정보, 업로드 패턴), "
        "댓글·대댓글(텍스트, 작성 시각, 참여지표), 댓글작성자-영상제작자 관계망이다."
    )

    doc.save(KOR_DOC)


def polish_eng() -> None:
    doc = Document(ENG_DOC)

    doc.paragraphs[5].text = (
        "This project begins in 2015 because the Paris Agreement provides the key institutional "
        "reference point for climate politics. It distinguishes 2020 as the threshold of fuller "
        "implementation. The period is shaped by carbon-neutrality agendas, climate-crisis framing, "
        "the expanding role of non-state actors, debates over just transition, and the instability "
        "of international cooperation. Distinguishing 2015 from 2020 makes it possible to compare "
        "a phase of transition and expectation with a phase of implementation, adjustment, and "
        "contestation."
    )

    doc.paragraphs[22].text = (
        "Data will be collected from the publicly searchable area of YouTube through the official "
        "YouTube API from December 12, 2015 to January 27, 2026. The starting point marks the "
        "adoption of the Paris Agreement, the key institutional reference point of the study, and "
        "the end point is the effective date of the U.S. withdrawal from the Paris Agreement, "
        "providing a clear political boundary for the corpus. Search terms will center on climate "
        "change and closely related Korean variants. The units of analysis are videos, channels, "
        "comments and replies, and commenter-creator ties, with videos organized through titles, "
        "descriptions, tags, captions or transcripts, and engagement indicators, and comments through "
        "text, timestamps, and participation measures. Korean-language content tied to South Korean "
        "channels, audiences, or policy contexts will define the operational scope of the corpus."
    )

    doc.save(ENG_DOC)


def verify() -> None:
    kor = Document(KOR_DOC)
    eng = Document(ENG_DOC)

    kor_text = "\n".join(p.text for p in kor.paragraphs)
    eng_text = "\n".join(p.text for p in eng.paragraphs)

    assert "국문 제목에서의" not in kor_text
    assert "the Korean title describes" not in eng_text
    assert "2015년 12월 12일부터 2026년 1월 27일까지 한국 유튜브의" not in kor_text
    assert "RQ1. What topics and frames emerge" in eng_text


def main() -> None:
    read_references()
    backup_files()
    polish_kor()
    polish_eng()
    verify()
    print("Backups updated:")
    print(KOR_BACKUP)
    print(ENG_BACKUP)


if __name__ == "__main__":
    main()
