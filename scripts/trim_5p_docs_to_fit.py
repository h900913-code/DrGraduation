from pathlib import Path
import shutil

from docx import Document


BASE = Path("WhatIWrote")
DOCX = BASE / "docx"


FILES = [
    (
        DOCX / "Doctoral_Research_Plan_5p_KOR.docx",
        DOCX / "Doctoral_Research_Plan_5p_KOR.backup_before_trim_revision.docx",
        {
            "월 단위를 기본 수집 단위로 설정하되 결과량이 많은 구간은 더 세분화해 누락을 줄인다. ": "",
            "사회적·정책적으로는 어떤 이슈와 메시지가 어떤 정서와 반응 구조를 통해 증폭되고, 어떤 행위자 구성이 갈등을 심화하거나 숙의를 가능하게 하는지 보여줌으로써 공공 커뮤니케이션 전략 수립에 기여할 수 있다. 더 나아가 이 연구는 한국 사회에서 신기후체제가 현재 어떤 상태에 놓여 있는지, 어디에서 취약성이 드러나는지, 목표 달성을 위해 어떤 담론적·정치적·소통적 조건이 필요한지를 논의하는 경험적 기반을 제공할 것이다. 반복적으로 등장하는 주장 서사와 오해 유형을 체계화한다는 점에서 미디어 리터러시와 환경교육 자료로의 활용 가능성도 기대된다.": "사회적·정책적으로는 어떤 이슈와 메시지가 어떤 정서와 반응 구조를 통해 증폭되고, 어떤 행위자 구성이 갈등을 심화하거나 숙의를 가능하게 하는지 보여줌으로써 공공 커뮤니케이션과 정책 논의에 기여할 수 있다. 더 나아가 이 연구는 한국 사회에서 신기후체제가 현재 어떤 상태에 놓여 있는지, 어디에서 취약성이 드러나는지, 목표 달성을 위해 어떤 담론적·정치적·소통적 조건이 필요한지를 논의하는 경험적 기반을 제공할 것이다.",
        },
    ),
    (
        DOCX / "Doctoral_Research_Plan_5p_ENG.docx",
        DOCX / "Doctoral_Research_Plan_5p_ENG.backup_before_trim_revision.docx",
        {
            "Monthly collection will serve as the default strategy, with finer segmentation in periods of heavy volume. ": "",
            "Socially and politically, the resulting discourse map can support public communication, media literacy, climate education, and policy discussion by showing which issues, emotions, and actor configurations intensify conflict, justify delay, or enable more constructive engagement. In that sense, the study does not stop at describing discursive patterns. It also provides evidence for assessing the fragilities of climate politics in South Korea and for discussing the communicative conditions under which climate goals can be sustained.": "Socially and politically, the resulting discourse map can support public communication and policy discussion by showing which issues, emotions, and actor configurations intensify conflict, justify delay, or enable more constructive engagement. It also provides evidence for assessing the fragilities of climate politics in South Korea and for discussing the communicative conditions under which climate goals can be sustained.",
        },
    ),
]


for docx_path, backup_path, replacements in FILES:
    if not backup_path.exists():
        shutil.copy2(docx_path, backup_path)

    doc = Document(docx_path)
    changed = 0
    for paragraph in doc.paragraphs:
        text = paragraph.text
        new_text = text
        for old, new in replacements.items():
            if old in new_text:
                new_text = new_text.replace(old, new)
        if new_text != text:
            paragraph.text = new_text
            changed += 1

    doc.save(docx_path)
    print(f"{docx_path.name}: updated {changed} paragraphs")
