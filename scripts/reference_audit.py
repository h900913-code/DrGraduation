from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

from docx import Document


BASE = Path("WhatIWrote")
OUT_CSV = BASE / "reference_audit.csv"
OUT_MD = BASE / "reference_audit_summary.md"

DOCS = [
    BASE / "Doctoral_Research_Plan_5p_KOR.docx",
    BASE / "Doctoral_Research_Plan_5p_ENG.docx",
    BASE / "Doctoral_Research_Plan_Full_KOR.docx",
]


SOURCE_INFO = {
    "allgaier2019": {
        "availability": "원문확인(저장소)",
        "notes": "Potential Papers/by_region/pdf_region/Europe/Germany/...Allgaier (2019)...pdf",
    },
    "beck1992": {
        "availability": "서지정보/요약확인(외부)",
        "notes": "외부 서지/도서 요약 페이지로만 확인",
    },
    "blei2003": {
        "availability": "초록/서지확인(외부)",
        "notes": "JMLR 페이지 기준 확인",
    },
    "boyd2012": {
        "availability": "초록/서지확인(외부)",
        "notes": "출판사/초록 페이지 기준 확인",
    },
    "denadal2024": {
        "availability": "원문확인(저장소)",
        "notes": "Potential Papers/by_region/pdf_region/Europe/United Kingdom/...de Nadal (2024)...pdf",
    },
    "douglas1982": {
        "availability": "서지정보/요약확인(외부)",
        "notes": "출판사/도서 설명 기준 확인",
    },
    "elgammal2026": {
        "availability": "원문확인(저장소)",
        "notes": "Potential Papers/data/text/...Elgammal et al. (2026)...txt",
    },
    "franzke2020": {
        "availability": "원문확인(저장소)",
        "notes": "Reference/Franzke, Bechmann, Zimmer, Ess, & Association of Internet Researchers. (2020)...pdf",
    },
    "grootendorst2022": {
        "availability": "초록/서지확인(외부)",
        "notes": "arXiv/서지 페이지 기준 확인",
    },
    "hilgartner1988": {
        "availability": "서지정보/개념설명확인(외부)",
        "notes": "서지/개념 소개 자료 기준 확인",
    },
    "ipcc2023": {
        "availability": "공식서지확인(외부)",
        "notes": "IPCC 공식 페이지 기준 확인",
    },
    "lamb2020": {
        "availability": "원문확인(저장소)",
        "notes": "Potential Papers/by_region/notes/Europe/Germany/...Lamb et al. (2020)...md",
    },
    "lim2021": {
        "availability": "초록/서지확인(외부)",
        "notes": "국내 DB 초록/서지 기준 확인",
    },
    "lim2023": {
        "availability": "초록/서지확인(외부)",
        "notes": "국내 DB 초록/서지 기준 확인",
    },
    "mohammad2016": {
        "availability": "서지정보만확인(외부)",
        "notes": "ACL Anthology 서지 페이지 기준 확인",
    },
    "newman2010": {
        "availability": "초록/서지확인(외부)",
        "notes": "OUP/서지 페이지 기준 확인",
    },
    "pang2008": {
        "availability": "초록/서지확인(외부)",
        "notes": "Now Publishers 페이지 기준 확인",
    },
    "shapiro2018": {
        "availability": "서지정보만확인(외부)",
        "notes": "서지/기관 소개 페이지 기준 확인",
    },
    "traag2019": {
        "availability": "초록/서지확인(외부)",
        "notes": "Nature article page 기준 확인",
    },
    "unfccc2015": {
        "availability": "공식서지확인(외부)",
        "notes": "UNFCCC 공식 문서 기준 확인",
    },
}


def canon_from_citation(text: str) -> str | None:
    s = text.lower().replace("–", "-").replace("—", "-")
    s = s.replace(".", "").replace(",", "")
    s = " ".join(s.split())
    checks = [
        ("beck", "1992", "beck1992"),
        ("hilgartner", "1988", "hilgartner1988"),
        ("allgaier", "2019", "allgaier2019"),
        ("shapiro", "2018", "shapiro2018"),
        ("임연수 외", "2021", "lim2021"),
        ("임연수 이기영 이진균", "2021", "lim2021"),
        ("lim et al", "2021", "lim2021"),
        ("lim y", "2021", "lim2021"),
        ("lim y lee g lee j", "2021", "lim2021"),
        ("임연수", "2023", "lim2023"),
        ("lim y", "2023", "lim2023"),
        ("lim 2023", "2023", "lim2023"),
        ("franzke", "2020", "franzke2020"),
        ("blei", "2003", "blei2003"),
        ("pang", "2008", "pang2008"),
        ("newman", "2010", "newman2010"),
        ("traag", "2019", "traag2019"),
        ("douglas", "1982", "douglas1982"),
        ("de nadal", "2024", "denadal2024"),
        ("elgammal", "2026", "elgammal2026"),
        ("lamb", "2020", "lamb2020"),
        ("grootendorst", "2022", "grootendorst2022"),
        ("mohammad", "2016", "mohammad2016"),
        ("boyd", "2012", "boyd2012"),
        ("ipcc", "2023", "ipcc2023"),
        ("unfccc", "2015", "unfccc2015"),
        ("united nations framework convention on climate change", "2015", "unfccc2015"),
    ]
    for name, year, canon in checks:
        if name in s and year in s:
            return canon
    return None


def canon_from_reference(text: str) -> str | None:
    return canon_from_citation(text)


def extract_doc(path: Path) -> dict:
    doc = Document(path)
    section = ""
    in_refs = False
    citation_rows = []
    references = {}
    ref_heading = None

    for idx, para in enumerate(doc.paragraphs):
        t = para.text.strip()
        if not t:
            continue
        if t in {"References", "참고문헌"}:
            in_refs = True
            ref_heading = t
            section = t
            continue
        if in_refs:
            canon = canon_from_reference(t)
            if canon:
                references[canon] = t
            continue
        if re.match(r"^\d+(\.\d+)?\s", t):
            section = t
        groups = re.findall(r"\(([^)]*\d{4}[^)]*)\)", t)
        for group in groups:
            for item in [p.strip() for p in group.split(";")]:
                canon = canon_from_citation(item)
                if canon:
                    citation_rows.append(
                        {
                            "document": path.name,
                            "section": section,
                            "paragraph_index": idx,
                            "paragraph_text": t,
                            "citation_item": item,
                            "canon": canon,
                        }
                    )
    return {
        "document": path.name,
        "citations": citation_rows,
        "references": references,
        "ref_heading": ref_heading or "",
    }


def pid(idx: int, text: str) -> str:
    snippet = text[:70].replace("\n", " ")
    return f"P{idx} | {snippet}"


PARA_CLAIMS = {
    ("Doctoral_Research_Plan_5p_KOR.docx", 4): {
        "claim": "기후변화 담론을 사회적으로 구성되고 공론장에서 재의미화되는 환경위험 이슈로 설명한다.",
        "type": "개념정의/배경설명",
    },
    ("Doctoral_Research_Plan_5p_KOR.docx", 7): {
        "claim": "한국 유튜브를 영상-댓글 연계 분석에 적합한 공간으로 설명하고 국내 선행연구의 주제 구조·용어 탐색을 호출한다.",
        "type": "선행연구/플랫폼설정",
    },
    ("Doctoral_Research_Plan_5p_KOR.docx", 23): {
        "claim": "검색 기반 유튜브 자료 수집의 재현가능성 기록과 연구윤리 원칙을 설명한다.",
        "type": "연구윤리/자료수집",
    },
    ("Doctoral_Research_Plan_5p_KOR.docx", 26): {
        "claim": "영상·댓글 텍스트에 확률 기반 토픽모형과 군집화 기법을 적용해 담론 변화를 추적한다.",
        "type": "방법론",
    },
    ("Doctoral_Research_Plan_5p_KOR.docx", 29): {
        "claim": "댓글의 정서와 태도를 사전 기반·지도학습·인적 검토로 분류하는 설계를 설명한다.",
        "type": "방법론",
    },
    ("Doctoral_Research_Plan_5p_KOR.docx", 32): {
        "claim": "댓글작성자-영상제작자 이분 네트워크에 중심성·커뮤니티 탐지를 적용하는 설계를 설명한다.",
        "type": "방법론",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 4): {
        "claim": "The paragraph defines climate discourse as a socially constructed risk issue renegotiated in public arenas.",
        "type": "conceptual definition/background",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 7): {
        "claim": "The paragraph presents South Korean YouTube as a suitable site for video-comment analysis and cites Korean prior studies on topic structure and terminology.",
        "type": "prior research/platform framing",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 23): {
        "claim": "The paragraph justifies reproducibility documentation and ethical precautions for search-based YouTube data collection.",
        "type": "research ethics/data collection",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 26): {
        "claim": "The paragraph proposes probabilistic topic modeling and related clustering for video and comment texts.",
        "type": "methodology",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 29): {
        "claim": "The paragraph proposes sentiment and attitude classification using dictionary methods, supervised models, and manual validation.",
        "type": "methodology",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 32): {
        "claim": "The paragraph proposes a bipartite commenter-creator network analyzed with centrality and community-detection techniques.",
        "type": "methodology",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 4): {
        "claim": "기후변화를 공론장에서 재의미화되는 환경위험이자 사회적 구성의 산물로 설명한다.",
        "type": "개념정의/배경설명",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 6): {
        "claim": "2015년 파리협정 채택을 신기후체제의 기준점으로 설정해 시기 구분의 출발점을 설명한다.",
        "type": "연구범위/시기설정",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 7): {
        "claim": "유튜브의 플랫폼 특성과 국외·국내 선행연구를 구분해 제시하면서 한국 장기 통합연구의 공백을 설명한다.",
        "type": "선행연구/플랫폼설정",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 22): {
        "claim": "시간 구획의 사건 기반 소구획 설정에서 IPCC 종합보고서와 같은 국제 평가 문서를 기준점으로 포함한다.",
        "type": "연구설계/시간구획",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 32): {
        "claim": "토픽 분석에서 LDA와 임베딩 기반 군집화(BERTopic)를 병행할 계획을 설명한다.",
        "type": "방법론",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 33): {
        "claim": "댓글의 정서와 입장 요소를 코드북 기반으로 분류하고 지연 담론 범주를 보조적으로 해석하는 설계를 설명한다.",
        "type": "방법론",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 34): {
        "claim": "이분 네트워크, 중심성, 커뮤니티 탐지로 행위자 결집 구조를 비교하는 설계를 설명한다.",
        "type": "방법론",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 43): {
        "claim": "공개 디지털 자료의 가명처리, 재식별 통제, 인용 최소화, IRB 점검 등 윤리 원칙을 설명한다.",
        "type": "연구윤리",
    },
}


EVALS = {
    ("Doctoral_Research_Plan_5p_KOR.docx", 4, "beck1992"): {
        "support_rating": "부분 지지",
        "rationale": "Beck는 환경위험과 위험사회의 사회적 성격을 뒷받침하지만, 문단의 핵심인 공론장 재의미화와 의미 경쟁까지 직접 설명하지는 않는다.",
        "recommended_action": "문장 축소 또는 공론장/담론구성 문헌 추가",
        "confidence": "medium",
        "notes": "",
    },
    ("Doctoral_Research_Plan_5p_KOR.docx", 4, "hilgartner1988"): {
        "support_rating": "직접 지지",
        "rationale": "Hilgartner와 Bosk의 public arenas model은 사회문제가 공론장에서 경쟁적으로 구성된다는 핵심 개념을 직접 제공한다.",
        "recommended_action": "유지",
        "confidence": "medium",
        "notes": "",
    },
    ("Doctoral_Research_Plan_5p_KOR.docx", 7, "allgaier2019"): {
        "support_rating": "부분 지지",
        "rationale": "Allgaier는 유튜브를 기후 커뮤니케이션과 왜곡 정보 유통의 핵심 장으로 다루므로 플랫폼 적합성은 지지한다. 다만 댓글 연계성과 한국 범위는 다른 문헌에 더 의존한다.",
        "recommended_action": "유지 가능하나 댓글 연계성 근거는 Shapiro에 더 의존",
        "confidence": "high",
        "notes": "저장소 원문 확인",
    },
    ("Doctoral_Research_Plan_5p_KOR.docx", 7, "shapiro2018"): {
        "support_rating": "직접 지지",
        "rationale": "Shapiro와 Park은 유튜브의 post-video discussion을 다루므로 영상 발화와 댓글 반응의 연계성을 직접 뒷받침한다.",
        "recommended_action": "유지",
        "confidence": "low",
        "notes": "원문 미보유; 외부 서지만 확인",
    },
    ("Doctoral_Research_Plan_5p_KOR.docx", 7, "lim2021"): {
        "support_rating": "직접 지지",
        "rationale": "임연수 외(2021)는 한국 유튜브에서 기후 관련 용어 차이와 공공커뮤니케이션 맥락을 다루므로 국내 선행연구의 용어 탐색을 직접 지지한다.",
        "recommended_action": "유지",
        "confidence": "medium",
        "notes": "",
    },
    ("Doctoral_Research_Plan_5p_KOR.docx", 7, "lim2023"): {
        "support_rating": "직접 지지",
        "rationale": "임연수(2023)는 기후변화 관련 유튜브 콘텐츠의 토픽모델링을 다루므로 국내 선행연구의 주제 구조 탐색을 직접 지지한다.",
        "recommended_action": "유지",
        "confidence": "medium",
        "notes": "",
    },
    ("Doctoral_Research_Plan_5p_KOR.docx", 23, "franzke2020"): {
        "support_rating": "직접 지지",
        "rationale": "AoIR 윤리 가이드라인은 온라인 자료의 식별자 처리, 인용 방식, 위험 평가, 연구심의 검토를 직접 다룬다.",
        "recommended_action": "유지",
        "confidence": "high",
        "notes": "저장소 원문 확인",
    },
    ("Doctoral_Research_Plan_5p_KOR.docx", 26, "blei2003"): {
        "support_rating": "직접 지지",
        "rationale": "Blei et al.은 LDA의 대표 원전으로, 확률 기반 토픽모형을 쓰겠다는 방법론 설명을 직접 뒷받침한다.",
        "recommended_action": "유지",
        "confidence": "high",
        "notes": "",
    },
    ("Doctoral_Research_Plan_5p_KOR.docx", 29, "pang2008"): {
        "support_rating": "부분 지지",
        "rationale": "Pang과 Lee는 sentiment/opinion mining의 고전적 개관으로 정서 분석 방법론은 지지한다. 다만 본문이 제시한 태도·책임귀속·지연 정당화 범주는 이 문헌만으로는 충분히 직접적이지 않다.",
        "recommended_action": "태도/stance 전용 문헌 추가",
        "confidence": "high",
        "notes": "",
    },
    ("Doctoral_Research_Plan_5p_KOR.docx", 32, "newman2010"): {
        "support_rating": "직접 지지",
        "rationale": "Newman은 이분 네트워크와 중심성 지표를 포함한 일반 네트워크 분석의 핵심 입문서로, 해당 방법론 설명을 직접 뒷받침한다.",
        "recommended_action": "유지",
        "confidence": "medium",
        "notes": "Full_KOR와 동일한 참고문헌 조합으로 정렬됨",
    },
    ("Doctoral_Research_Plan_5p_KOR.docx", 32, "traag2019"): {
        "support_rating": "직접 지지",
        "rationale": "Traag et al.은 Leiden community detection의 핵심 문헌으로, 커뮤니티 탐지 기법 사용을 직접 뒷받침한다.",
        "recommended_action": "유지",
        "confidence": "high",
        "notes": "",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 4, "beck1992"): {
        "support_rating": "부분 지지",
        "rationale": "Beck supports the broader claim that environmental risk is socially organized, but it does not itself supply the public-arena model invoked in the sentence.",
        "recommended_action": "narrow wording or add a more direct discourse-construction source",
        "confidence": "medium",
        "notes": "",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 4, "hilgartner1988"): {
        "support_rating": "직접 지지",
        "rationale": "Hilgartner and Bosk directly theorize social problems as competitively constructed in public arenas, which fits the sentence's core framing.",
        "recommended_action": "maintain",
        "confidence": "medium",
        "notes": "",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 7, "allgaier2019"): {
        "support_rating": "부분 지지",
        "rationale": "Allgaier directly supports YouTube as an important climate communication venue and a site of distorted climate communication, but the comment-linkage and South Korean scope rely on other sources.",
        "recommended_action": "maintain; rely on Shapiro for comment linkage",
        "confidence": "high",
        "notes": "local full text available in repository",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 7, "shapiro2018"): {
        "support_rating": "직접 지지",
        "rationale": "Shapiro and Park directly support the linkage between video messages and post-video comment discussion on YouTube.",
        "recommended_action": "maintain",
        "confidence": "low",
        "notes": "external bibliographic confirmation only",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 7, "lim2021"): {
        "support_rating": "직접 지지",
        "rationale": "The 2021 Korean YouTube study directly supports the prior-work claim about terminology differences in local climate-related YouTube content.",
        "recommended_action": "maintain",
        "confidence": "medium",
        "notes": "",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 7, "lim2023"): {
        "support_rating": "직접 지지",
        "rationale": "The 2023 Korean YouTube study uses topic modeling on climate-related YouTube content, so it directly supports the claim about prior work on topic structure.",
        "recommended_action": "maintain",
        "confidence": "medium",
        "notes": "",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 23, "franzke2020"): {
        "support_rating": "직접 지지",
        "rationale": "The AoIR guidelines directly address ethical handling, quotation minimization, risk assessment, and review considerations for internet research.",
        "recommended_action": "maintain",
        "confidence": "high",
        "notes": "local source available",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 26, "blei2003"): {
        "support_rating": "직접 지지",
        "rationale": "Blei et al. is the canonical source for LDA and directly supports the use of probabilistic topic modeling.",
        "recommended_action": "maintain",
        "confidence": "high",
        "notes": "",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 29, "pang2008"): {
        "support_rating": "부분 지지",
        "rationale": "Pang and Lee strongly support sentiment analysis, but the paragraph's attitude and delay-justification categories go beyond what this citation alone directly grounds.",
        "recommended_action": "add stance/attitude citation",
        "confidence": "high",
        "notes": "",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 32, "newman2010"): {
        "support_rating": "직접 지지",
        "rationale": "Newman provides the general network-analysis foundation for bipartite structure and centrality measures used in the paragraph.",
        "recommended_action": "maintain",
        "confidence": "medium",
        "notes": "aligned with KOR 5p and Full_KOR",
    },
    ("Doctoral_Research_Plan_5p_ENG.docx", 32, "traag2019"): {
        "support_rating": "직접 지지",
        "rationale": "Traag et al. directly support the community-detection component of the paragraph, and the remaining centrality claim is now covered by Newman.",
        "recommended_action": "maintain",
        "confidence": "high",
        "notes": "paired with Newman for full methods coverage",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 4, "beck1992"): {
        "support_rating": "부분 지지",
        "rationale": "Beck는 환경위험과 근대사회의 위험 구조를 설명하지만, 문단의 공론장 재의미화와 의미 경쟁은 별도 이론이 더 직접적이다.",
        "recommended_action": "문장 축소 또는 공론장 문헌과 역할 분리",
        "confidence": "medium",
        "notes": "",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 4, "douglas1982"): {
        "support_rating": "부분 지지",
        "rationale": "Douglas와 Wildavsky는 위험 인식의 문화적 선택을 설명하므로 사회적 구성 측면은 지지한다. 다만 문단의 공론장 경쟁과 담론 구성 전체를 직접 설명하지는 않는다.",
        "recommended_action": "문장 축소 또는 개념별 인용 분리",
        "confidence": "low",
        "notes": "",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 4, "hilgartner1988"): {
        "support_rating": "직접 지지",
        "rationale": "공론장에서 사회문제가 구성·경쟁된다는 핵심 명제는 본 문단의 문제의식과 직접적으로 부합한다.",
        "recommended_action": "유지",
        "confidence": "medium",
        "notes": "",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 6, "unfccc2015"): {
        "support_rating": "직접 지지",
        "rationale": "UNFCCC의 Paris Agreement 원문은 2015년이 새로운 국제 기후 거버넌스 기준점이라는 시기 구분의 근거를 직접 제공한다.",
        "recommended_action": "유지",
        "confidence": "high",
        "notes": "공식 문서",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 7, "allgaier2019"): {
        "support_rating": "부분 지지",
        "rationale": "Allgaier는 유튜브가 기후 왜곡 커뮤니케이션의 중요한 장이라는 점을 직접 보여주므로 플랫폼 적합성은 지지한다. 다만 한국 범위의 장기 통합연구 공백 자체를 직접 입증하지는 않는다.",
        "recommended_action": "플랫폼 적합성 근거로 유지",
        "confidence": "high",
        "notes": "저장소 원문 확인",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 7, "denadal2024"): {
        "support_rating": "부분 지지",
        "rationale": "de Nadal은 유튜브에서 기후 허위정보와 정치적 문화전쟁이 전개되는 국외 사례를 직접 보여주므로 비교 사례 근거로는 적절하다. 다만 한국 장기 통합연구 공백의 직접 근거는 아니다.",
        "recommended_action": "비교사례 문헌으로 유지",
        "confidence": "high",
        "notes": "저장소 원문 확인",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 7, "shapiro2018"): {
        "support_rating": "직접 지지",
        "rationale": "Shapiro와 Park은 기후 유튜브의 post-video discussion을 직접 다루므로 영상 발화와 댓글 반응을 함께 관찰할 수 있다는 주장에 직접 부합한다.",
        "recommended_action": "유지",
        "confidence": "medium",
        "notes": "원문 미보유; 외부 서지 기준",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 7, "lim2021"): {
        "support_rating": "직접 지지",
        "rationale": "임연수 외(2021)는 한국 유튜브에서 기후 관련 용어와 공공커뮤니케이션 방향을 다루므로 국내 선행연구의 용어·주제 차이 탐색을 직접 뒷받침한다.",
        "recommended_action": "유지",
        "confidence": "medium",
        "notes": "",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 7, "lim2023"): {
        "support_rating": "직접 지지",
        "rationale": "임연수(2023)는 기후변화 관련 유튜브 콘텐츠의 토픽모델링을 다루므로 국내 선행연구의 주제 구조 탐색을 직접 지지한다.",
        "recommended_action": "유지",
        "confidence": "medium",
        "notes": "",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 22, "ipcc2023"): {
        "support_rating": "직접 지지",
        "rationale": "IPCC 2023 종합보고서는 시간 구획의 기준점으로 활용할 수 있는 대표적 국제 평가 문서다.",
        "recommended_action": "유지",
        "confidence": "high",
        "notes": "공식 문서",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 32, "blei2003"): {
        "support_rating": "직접 지지",
        "rationale": "LDA의 대표 원전으로서 확률 기반 토픽모형 사용을 직접 뒷받침한다.",
        "recommended_action": "유지",
        "confidence": "high",
        "notes": "",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 32, "grootendorst2022"): {
        "support_rating": "직접 지지",
        "rationale": "BERTopic은 임베딩 기반 토픽/군집화 절차의 대표 문헌이므로 본문 설명과 직접 부합한다.",
        "recommended_action": "유지",
        "confidence": "medium",
        "notes": "",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 33, "pang2008"): {
        "support_rating": "부분 지지",
        "rationale": "Pang과 Lee는 정서 및 의견 분석의 일반 방법론을 직접 뒷받침한다. 다만 구체적인 기후 담론 범주는 별도 문헌과 코드북 설계가 필요하다.",
        "recommended_action": "유지",
        "confidence": "high",
        "notes": "",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 33, "mohammad2016"): {
        "support_rating": "부분 지지",
        "rationale": "Mohammad et al.은 지도학습 기반 stance detection과 인적 검토 절차의 일반 틀을 제공하므로 입장 분류 설계의 방법론적 골격을 지지한다. 다만 매체와 주제가 달라 기후 유튜브 댓글 자\ccb4를 직접 입증하지는 않는다.",
        "recommended_action": "유지",
        "confidence": "medium",
        "notes": "",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 33, "elgammal2026"): {
        "support_rating": "직접 지지",
        "rationale": "Elgammal et al.은 기후변화 이슈에 관한 YouTube 댓글을 대상으로 sentiment analysis를 수행하므로, 해당 문단의 댓글 정서 분석 설계를 직접 뒷받침한다.",
        "recommended_action": "유지",
        "confidence": "high",
        "notes": "저장소 원문 확인",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 33, "lamb2020"): {
        "support_rating": "직접 지지",
        "rationale": "Lamb et al.은 climate delay discourse의 유형화를 제시하므로, 지연 담론 단서를 보조적 해석 범주로 삼는 설계를 직접 지지한다.",
        "recommended_action": "유지",
        "confidence": "high",
        "notes": "저장소 원문 확인",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 34, "newman2010"): {
        "support_rating": "직접 지지",
        "rationale": "Newman은 네트워크 분석의 기본 개념과 중심성 지표를 제공하므로 해당 방법론 설명을 직접 뒷받침한다.",
        "recommended_action": "유지",
        "confidence": "medium",
        "notes": "",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 34, "traag2019"): {
        "support_rating": "직접 지지",
        "rationale": "Leiden community detection의 핵심 문헌으로서 커뮤니티 탐지 부분을 직접 지지한다.",
        "recommended_action": "유지",
        "confidence": "high",
        "notes": "",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 43, "franzke2020"): {
        "support_rating": "직접 지지",
        "rationale": "인터넷 연구 윤리 가이드라인으로서 가명처리, 위험 통제, 인용 최소화, 심의 검토를 직접적으로 뒷받침한다.",
        "recommended_action": "유지",
        "confidence": "high",
        "notes": "저장소 원문 확인",
    },
    ("Doctoral_Research_Plan_Full_KOR.docx", 43, "boyd2012"): {
        "support_rating": "간접 지지",
        "rationale": "boyd와 Crawford는 빅데이터 연구의 비판적 질문을 제기하므로 윤리·방법론적 주의의식은 지지한다. 그러나 AoIR 가이드라인처럼 구체적 인터넷 연구 윤리 절차를 직접 제시하지는 않는다.",
        "recommended_action": "보조 문헌으로만 유지하거나 역할 축소",
        "confidence": "medium",
        "notes": "표기 스타일도 다른 참고문헌과 다름",
    },
}


TOP_ISSUES = [
    ("Doctoral_Research_Plan_5p_KOR.docx", 7, "allgaier2019"),
    ("Doctoral_Research_Plan_5p_ENG.docx", 7, "allgaier2019"),
    ("Doctoral_Research_Plan_Full_KOR.docx", 7, "denadal2024"),
    ("Doctoral_Research_Plan_Full_KOR.docx", 7, "allgaier2019"),
    ("Doctoral_Research_Plan_Full_KOR.docx", 43, "boyd2012"),
]


def build_rows():
    extracted = {doc.name: extract_doc(doc) for doc in DOCS}
    rows = []
    citation_counts = {}
    reference_counts = {}
    cited_by_doc = defaultdict(set)

    for doc_name, data in extracted.items():
        citation_counts[doc_name] = len(data["citations"])
        reference_counts[doc_name] = len(data["references"])
        for item in data["citations"]:
            key = (doc_name, item["paragraph_index"], item["canon"])
            claim_meta = PARA_CLAIMS[(doc_name, item["paragraph_index"])]
            eval_meta = EVALS[key]
            matched_ref = data["references"].get(item["canon"], "")
            cited_by_doc[doc_name].add(item["canon"])
            rows.append(
                {
                    "document": doc_name,
                    "section": item["section"],
                    "paragraph_identifier": pid(item["paragraph_index"], item["paragraph_text"]),
                    "cited_sentence_or_claim": claim_meta["claim"],
                    "citation_marker_or_reference": item["citation_item"],
                    "matched_reference_full": matched_ref,
                    "claim_type": claim_meta["type"],
                    "support_rating": eval_meta["support_rating"],
                    "rationale": eval_meta["rationale"],
                    "recommended_action": eval_meta["recommended_action"],
                    "confidence": eval_meta["confidence"],
                    "source_availability": SOURCE_INFO[item["canon"]]["availability"],
                    "notes": (eval_meta["notes"] + (" | " if eval_meta["notes"] else "") + SOURCE_INFO[item["canon"]]["notes"]).strip(" |"),
                }
            )

    # listed but not cited
    for doc_name, data in extracted.items():
        for canon, ref in data["references"].items():
            if canon not in cited_by_doc[doc_name]:
                rows.append(
                    {
                        "document": doc_name,
                        "section": data["ref_heading"] or "References",
                        "paragraph_identifier": "reference-only",
                        "cited_sentence_or_claim": "본문 인용이 없어 지지 적합성을 평가할 대상 문장이 없다.",
                        "citation_marker_or_reference": "not cited in body",
                        "matched_reference_full": ref,
                        "claim_type": "reference_list_only",
                        "support_rating": "확인 불충분",
                        "rationale": "참고문헌 목록에는 있으나 본문에서 실제로 호출되지 않아, 특정 주장과의 적합성을 평가할 수 없다.",
                        "recommended_action": "인용 추가 또는 목록 삭제",
                        "confidence": "high",
                        "source_availability": SOURCE_INFO[canon]["availability"],
                        "notes": "listed-not-cited | " + SOURCE_INFO[canon]["notes"],
                    }
                )

    return extracted, rows, citation_counts, reference_counts


def make_summary(extracted, rows, citation_counts, reference_counts):
    citation_rows = [r for r in rows if r["claim_type"] != "reference_list_only"]
    rating_counts = Counter(r["support_rating"] for r in citation_rows)
    listed_not_cited = [r for r in rows if r["claim_type"] == "reference_list_only"]
    cited_not_listed = [r for r in citation_rows if not r["matched_reference_full"]]

    row_lookup = {
        (r["document"], int(r["paragraph_identifier"].split("|")[0][1:].strip()), canon_from_citation(r["citation_marker_or_reference"]) or "")
        : r
        for r in citation_rows
    }
    top_rows = [row_lookup[k] for k in TOP_ISSUES if k in row_lookup]
    low_conf_rows = [r for r in citation_rows if r["confidence"] == "low"]

    lines = []
    lines.append("# Reference Audit Summary")
    lines.append("")
    lines.append("## 1) 전체 검토 대상 문서 목록")
    for doc in DOCS:
        lines.append(f"- {doc.name}")
    lines.append("")
    lines.append("## 2) 문서별 참고문헌 개수")
    for doc in DOCS:
        lines.append(f"- {doc.name}: {reference_counts[doc.name]}개")
    lines.append("")
    lines.append("## 3) 문서별 본문 인용 사례 개수")
    for doc in DOCS:
        lines.append(f"- {doc.name}: {citation_counts[doc.name]}건")
    lines.append("")
    lines.append("## 4) 지지 적합성 판정 건수 요약")
    for key in ["직접 지지", "부분 지지", "간접 지지", "부적합", "확인 불충분"]:
        lines.append(f"- {key}: {rating_counts.get(key, 0)}건")
    lines.append("")
    lines.append("## 5) 가장 문제 큰 사례 TOP 10")
    for idx, row in enumerate(top_rows[:10], start=1):
        lines.append(
            f"{idx}. {row['document']} | {row['section']} | {row['citation_marker_or_reference']} | {row['support_rating']} | {row['recommended_action']}"
        )
        lines.append(f"   - {row['cited_sentence_or_claim']}")
        lines.append(f"   - {row['rationale']}")
    if not top_rows:
        lines.append("- 해당 없음")
    lines.append("")
    lines.append("## 6) 참고문헌 목록에는 있는데 본문에서 안 쓰인 항목")
    if listed_not_cited:
        for row in listed_not_cited:
            lines.append(f"- {row['document']} | {row['matched_reference_full']}")
    else:
        lines.append("- 없음")
    lines.append("")
    lines.append("## 7) 본문에서 인용된 듯하나 참고문헌에 없는 항목")
    if cited_not_listed:
        for row in cited_not_listed:
            lines.append(
                f"- {row['document']} | {row['citation_marker_or_reference']} | {row['section']} | {row['paragraph_identifier']}"
            )
    else:
        lines.append("- 없음")
    lines.append("")
    lines.append("## 8) 우선 수정이 필요한 문장/문단 제안")
    priority_notes = [
        "두 5페이지 문서의 서론 1. Introduction/연구 배경 P7은 Lim/임연수(2023)까지 호출해 국내 선행연구 근거를 보강했지만, 플랫폼 적합성 논증은 여전히 Allgaier·Shapiro 조합에 주로 의존한다.",
        "Doctoral_Research_Plan_Full_KOR.docx P7: 국외 YouTube 사례와 국내 연구 공백을 분리해 쓰는 현재 구조가 이전보다 적절하지만, 여전히 장기 통합연구 공백의 직접 근거는 국내 선행연구에 더 의존하는 편이 안전함.",
        "Doctoral_Research_Plan_Full_KOR.docx P43: boyd & Crawford는 보조 문헌으로는 가능하나 윤리 절차의 직접 근거는 Franzke et al.에 더 의존하는 편이 정확함.",
    ]
    for note in priority_notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## 9) 사람이 직접 원문을 다시 확인해야 할 사례 목록")
    if low_conf_rows:
        for row in low_conf_rows:
            lines.append(
                f"- {row['document']} | {row['citation_marker_or_reference']} | {row['section']} | {row['support_rating']} | {row['source_availability']}"
            )
    else:
        lines.append("- 없음")
    lines.append("")
    lines.append("## 10) 교차 문서 일관성 메모")
    lines.append("- 5p_KOR와 5p_ENG의 4.4는 Newman + Traag 조합으로 정렬되었다.")
    lines.append("- 5p_KOR와 5p_ENG 모두 Lim/임연수 (2023)를 P7 본문에서 직접 호출하도록 정렬되었다.")
    lines.append("- Full_KOR는 IPCC (2023), UNFCCC (2015)를 시간구획 설명 문단에서 직접 호출하도록 정렬되었다.")
    lines.append("- Full_KOR의 boyd, d. 표기는 다른 참고문헌과 달리 소문자 저자 표기를 사용해 스타일 불일치가 있음.")
    return "\n".join(lines), rating_counts, len(citation_rows), listed_not_cited, cited_not_listed


def main():
    extracted, rows, citation_counts, reference_counts = build_rows()

    fieldnames = [
        "document",
        "section",
        "paragraph_identifier",
        "cited_sentence_or_claim",
        "citation_marker_or_reference",
        "matched_reference_full",
        "claim_type",
        "support_rating",
        "rationale",
        "recommended_action",
        "confidence",
        "source_availability",
        "notes",
    ]

    with OUT_CSV.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    summary_text, rating_counts, citation_case_count, listed_not_cited, cited_not_listed = make_summary(
        extracted, rows, citation_counts, reference_counts
    )
    OUT_MD.write_text(summary_text, encoding="utf-8")

    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")
    print(f"citation_case_count={citation_case_count}")
    print(f"listed_not_cited={len(listed_not_cited)}")
    print(f"cited_not_listed={len(cited_not_listed)}")
    for key in ["직접 지지", "부분 지지", "간접 지지", "부적합", "확인 불충분"]:
        print(f"{key}={rating_counts.get(key, 0)}")


if __name__ == "__main__":
    main()
