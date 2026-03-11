from pathlib import Path
from shutil import copy2

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH


ROOT = Path(__file__).resolve().parents[1] / "WhatIWrote"


def backup(path: Path) -> None:
    if path.exists():
        copy2(path, path.with_name(path.stem + ".backup_before_dense_revision" + path.suffix))


def clear_body(doc: Document) -> None:
    body = doc._body._element
    for child in list(body):
        if child.tag.endswith("sectPr"):
            continue
        body.remove(child)


def add_entry(doc: Document, kind: str, text: str = "") -> None:
    p = doc.add_paragraph()
    if kind == "blank":
        return
    run = p.add_run(text)
    if kind == "title":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run.bold = True
    elif kind == "author":
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run.bold = True
    elif kind in {"heading", "ref_heading"}:
        run.bold = True


def rewrite(path: Path, entries: list[tuple[str, str]]) -> None:
    doc = Document(path)
    clear_body(doc)
    for kind, text in entries:
        add_entry(doc, kind, text)
    doc.save(path)


kor_entries = [
    ("title", "신기후체제하 한국 기후변화 담론 지형의 변동 분석 : 유튜브 영상댓글행위자 네트워크를 중심으로"),
    ("author", "Jeonghyeon Park"),
    ("blank", ""),
    ("heading", "1. 연구 배경 및 문제의식"),
    (
        "body",
        "기후변화는 과학적 사실이 알려진다고 해서 자동으로 사회적 합의로 이어지는 문제가 아니다. 기후위험은 책임 귀속, 정의, 전환 비용, 생활세계의 체감 경험이 뒤얽히는 가운데 공론장에서 끊임없이 재의미화되며, 따라서 기후담론 역시 정보의 양이나 정확성만으로 설명할 수 없는 사회적 구성물로 보아야 한다(Beck, 1992; Hilgartner & Bosk, 1988). 본 연구는 이러한 문제의식에서 출발하여 한국 사회의 기후변화 담론을 정적인 분포가 아니라 시간과 사건을 거치며 재편되는 관계적 지형으로 파악하고자 한다.",
    ),
    (
        "body",
        "이 연구에서 신기후체제는 파리협정 채택 이후 형성되고 2020년 이후 본격적인 이행 국면에 들어선 새로운 국제 기후거버넌스 질서를 뜻한다. 이 개념은 단순한 시기 구분이 아니라 파리협정의 제도적 틀, 탄소중립 의제의 확산, 기후위기 프레이밍의 강화, 비국가행위자의 참여 확대, 정의로운 전환을 둘러싼 갈등, 국제협력의 불안정성이 겹쳐지는 역사적 조건을 함께 가리킨다. 따라서 국문 제목에서의 “신기후체제하”는 단지 파리협정 이후를 뜻하는 표현이 아니라, 기후정치와 담론의 조건 자체가 새롭게 조직되는 국면을 분석 대상으로 삼겠다는 선언에 가깝다.",
    ),
    (
        "body",
        "이때 2015년과 2020년을 구분하는 것이 중요하다. 2015년은 파리협정 채택을 통해 새로운 기준점이 제시된 해이고, 2020년은 협정의 본격 적용과 이행 논리가 가시화되기 시작한 전환점이다. 이에 본 연구는 2015~2019년을 체제 형성과 기대의 축적 국면으로, 2020~2026년을 이행과 재조정의 국면으로 구분하고, 그 안에서 2016년 협정 발효, 2017년 미국 탈퇴 선언, 2021년 미국 재가입, COP, IPCC 보고서, NDC 갱신, 대형 기후재난, 국내 정책 및 정치 이벤트 전후를 세부 비교 단위로 설정한다. 이러한 시기 구획은 담론의 변동을 단순한 연도별 빈도 변화가 아니라 국면별 재편의 과정으로 읽기 위한 장치다.",
    ),
    (
        "body",
        "한국 유튜브는 이 문제를 분석하기에 적합한 공간이다. 과학 정보, 개인 경험, 정치적 주장, 허위·왜곡 정보가 한 플랫폼 안에서 함께 유통되고, 영상 발화와 댓글 반응을 연결해 관찰할 수 있기 때문이다(Allgaier, 2019; Shapiro & Park, 2018). 특히 유튜브는 추천과 개인화에 따라 노출 구조가 형성되지만, 검색으로 반복 확인 가능한 공개영역은 비교적 재현가능한 방식으로 장기 자료를 구축할 수 있게 해준다. 본 연구는 이러한 특성을 활용해 한국어로 생산·유통되며 한국 채널, 한국 공중, 한국의 기후·에너지·재난·정책 이슈와 실질적으로 연결된 유튜브 자료를 분석 대상으로 삼는다. 국내 연구는 한국 유튜브에서 기후 관련 콘텐츠의 주제 구조와 용어 차이를 탐색해 왔다(임연수 외, 2021; 임연수, 2023).",
    ),
    ("blank", ""),
    ("heading", "2. 연구 목적"),
    (
        "body",
        "이 연구의 목적은 신기후체제하 한국 기후변화 담론 지형의 구조와 변동을 통합적으로 설명하는 데 있다. 이를 위해 발화(영상), 반응(댓글), 결집(행위자 네트워크)의 세 층위를 하나의 시간축 위에서 연결하고, 토픽과 프레임의 이동, 정서 및 태도의 분화, 채널 중심 결집 구조의 변화를 함께 추적한다. 다시 말해 이 연구는 무엇이 말해졌는가만이 아니라 그 말이 어떤 반응을 낳고 누구를 중심으로 조직되는가를 동시에 살핌으로써, 한국 사회에서 기후담론이 어떤 조건에서 강화되거나 약화되는지를 드러내고자 한다.",
    ),
    ("blank", ""),
    ("heading", "3. 연구문제"),
    ("body", "이 연구는 다음의 연구문제를 중심으로 진행된다."),
    (
        "body",
        "RQ1. 2015년 12월 12일부터 2026년 1월 27일까지 한국 유튜브의 기후변화 관련 영상과 댓글에서는 어떤 주제와 프레임이 형성되며, 2015~2019년과 2020~2026년의 대구획 및 주요 사건 국면 전후에 그 담론 지형은 어떻게 재편되는가?",
    ),
    (
        "body",
        "RQ2. 댓글 담론의 반응 구조는 어떤 정서와 태도로 조직되며, 수용과 회의, 책임 귀속, 정책 찬반, 지연 정당화와 같은 반응 양상은 토픽과 시기, 사건 국면에 따라 어떻게 변화하는가?",
    ),
    (
        "body",
        "RQ3. 댓글작성자-영상제작자 관계를 중심으로 한 행위자 네트워크는 시기별로 어떻게 형성·변동하며, 어떤 채널과 행위자 집합이 특정 논점과 반응에 반복적으로 결집하는가? 이러한 변화는 신기후체제의 현재 상태와 취약성, 그리고 그 지속 조건을 읽는 데 어떤 단서를 제공하는가?",
    ),
    ("blank", ""),
    ("heading", "4. 연구방법"),
    (
        "body",
        "본 연구는 재현가능한 자료 수집과 기초통계, 토픽 분석, 정서·태도 분석, 행위자 네트워크 분석을 결합하는 혼합적 설계를 사용한다. 분석은 단일 시점의 스냅샷이 아니라 장기 시계열과 사건 기반 비교를 함께 다루는 방식으로 진행되며, 자료 규모와 분류 적합도를 고려해 지도학습과 비지도학습을 병행할 수 있다. 또한 공개 디지털 자료를 다루는 연구라는 점에서 수집 규칙의 문서화, 해석 가능 범위의 명시, 연구윤리 준수를 방법론의 일부로 포함한다.",
    ),
    ("blank", ""),
    ("heading", "4.1 자료 수집"),
    (
        "body",
        "자료는 유튜브 공식 API를 활용해 검색으로 반복 확인 가능한 공개영역에서 수집한다. 시간적 범위는 2015년 12월 12일부터 2026년 1월 27일까지이며, 기본 검색어는 “기후변화”를 중심으로 하되 띄어쓰기 변형과 관련 표현을 보조적으로 검토한다. 분석 단위는 영상(제목, 설명, 태그, 자막/전사, 참여지표), 채널(기본 정보, 업로드 패턴), 댓글·대댓글(텍스트, 작성 시각, 참여지표), 댓글작성자-영상제작자 관계망이다. 자막이 없는 영상은 가능한 범위에서 자동 음성 인식 전사를 활용하며, 자료는 시기별 비교가 가능하도록 구조화한다.",
    ),
    (
        "body",
        "재현가능성을 높이기 위해 수집 시점, 검색어, 정렬 기준, 기간 단위, 결과 상한 대응, 결측 처리 방식을 함께 기록한다. 월 단위를 기본 수집 단위로 설정하되 결과량이 많은 구간은 더 세분화해 누락을 줄인다. 또한 검색 기반 설계가 개인화 추천에 따라 형성되는 비검색 노출을 완전히 포착하지 못한다는 한계를 명시적으로 밝히고, 삭제·비공개·댓글 비활성화 상태는 별도 결측 상태로 관리한다. 식별자는 가명처리하고, 재식별 위험 통제와 원문 인용 최소화 원칙을 적용하며, IRB 또는 기관 심의 필요성을 사전에 점검한다(Franzke et al., 2020).",
    ),
    ("blank", ""),
    ("heading", "4.2 토픽 및 프레임 분석"),
    (
        "body",
        "토픽 및 프레임 분석은 영상 텍스트와 댓글 텍스트 모두에 적용한다. 이를 통해 기후위기, 탄소중립, 에너지 전환, 책임 귀속, 생활비 부담, 과학 신뢰, 정책 회의와 같은 주제 묶음이 각 시기와 사건 국면에서 어떻게 부상하고 약화되는지 추적한다. 분석에는 확률 기반 토픽모형과 임베딩 기반 군집화 기법을 비교 적용하고(Blei et al., 2003), 필요 시 대표 문서 검토를 병행하여 해석 가능한 수준의 프레임 묶음을 정리한다. 이 단계는 영상 담론의 이동과 댓글 반응의 이동이 어떤 지점에서 맞물리거나 어긋나는지를 보여주는 핵심 축이 된다.",
    ),
    ("blank", ""),
    ("heading", "4.3 정서 및 태도 분석"),
    (
        "body",
        "정서 및 태도 분석은 주로 댓글 자료를 중심으로 수행한다. 여기서는 분노, 불안, 냉소, 조롱, 희망과 같은 정서와, 과학 수용·회의, 책임 귀속, 정책 찬반, 지연 정당화와 같은 태도를 구분하여 파악한다. 사전 기반 접근과 지도학습 분류기, 기타 기계학습 기법을 비교 적용하되, 표본 자료에 대한 인적 검토를 통해 분류 적합도를 점검한다(Pang & Lee, 2008). 이를 통해 동일한 토픽이 시기별로 어떤 정서·태도 조합을 동반하는지, 그리고 사건 국면별로 어떤 반응 구조가 강화되거나 완화되는지를 설명할 수 있다.",
    ),
    ("blank", ""),
    ("heading", "4.4 행위자 네트워크 분석"),
    (
        "body",
        "행위자 네트워크 분석은 댓글작성자-영상제작자 이분 네트워크를 기본 구조로 삼는다. 이를 통해 어떤 채널이 반복적으로 반응을 집중시키는지, 어떤 참여자 집단이 특정 채널군과 결속하는지, 그리고 그 구성이 시기와 사건 국면에 따라 어떻게 이동하는지 파악한다. 필요할 경우 채널 간 연결, 댓글 공동참여 패턴, 영상과 댓글 속 주요 행위자의 공출현 관계를 보조 지표로 검토할 수 있다. 중심성 지표와 커뮤니티 탐지 기법을 활용해(Newman, 2010; Traag et al., 2019) 토픽과 정서·태도 분포가 어떤 행위자 결집 구조와 맞물리는지를 통합적으로 해석한다.",
    ),
    ("blank", ""),
    ("heading", "5. 기대효과 및 함의"),
    (
        "body",
        "학문적으로 이 연구는 한국 유튜브의 기후담론을 발화-반응-결집의 다층 구조로 장기 추적함으로써, 환경위험의 사회적 구성과 의미 경쟁을 디지털 공론장 자료에 근거해 실증적으로 확장한다. 특히 기존 연구에서 분절적으로 다뤄지던 내용 분석, 반응 분석, 관계 분석을 동일한 해석 틀로 연결하여, 사건 국면 전후의 담론 변동을 보다 입체적으로 설명하는 근거를 제공할 수 있다. 방법론적으로도 유튜브 공개자료를 장기 시계열 자료로 구축하고, 토픽 분석, 정서·태도 분석, 네트워크 분석을 동일 시간축에서 결합하는 재현가능한 절차를 제시한다.",
    ),
    (
        "body",
        "사회적·정책적으로는 어떤 이슈와 메시지가 어떤 정서와 반응 구조를 통해 증폭되고, 어떤 행위자 구성이 갈등을 심화하거나 숙의를 가능하게 하는지 보여줌으로써 공공 커뮤니케이션 전략 수립에 기여할 수 있다. 더 나아가 이 연구는 한국 사회에서 신기후체제가 현재 어떤 상태에 놓여 있는지, 어디에서 취약성이 드러나는지, 목표 달성을 위해 어떤 담론적·정치적·소통적 조건이 필요한지를 논의하는 경험적 기반을 제공할 것이다. 반복적으로 등장하는 주장 서사와 오해 유형을 체계화한다는 점에서 미디어 리터러시와 환경교육 자료로의 활용 가능성도 기대된다.",
    ),
    ("blank", ""),
    ("ref_heading", "참고문헌"),
]

kor_refs = [
    "Allgaier, J. (2019). Science and environmental communication on YouTube: Strategically distorted communications in online videos on climate change and climate engineering. Frontiers in Communication, 4, 36.",
    "Beck, U. (1992). Risk society: Towards a new modernity. Sage.",
    "Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet Allocation. Journal of Machine Learning Research, 3, 993-1022.",
    "Franzke, A. S., Bechmann, A., Zimmer, M., Ess, C., & Association of Internet Researchers. (2020). Internet research: Ethical guidelines 3.0. Association of Internet Researchers.",
    "Hilgartner, S., & Bosk, C. L. (1988). The rise and fall of social problems: A public arenas model. American Journal of Sociology, 94(1), 53-78.",
    "Newman, M. E. J. (2010). Networks: An introduction. Oxford University Press.",
    "임연수. (2023). 기후변화 관련 유튜브 콘텐츠에 대한 토픽모델링. 한국융합과학회지, 12(2), 139-150.",
    "임연수, 이기영, 이진균. (2021). 유튜브에서 “기후변화”, “기후위기”, “지구온난화”는 어떻게 다뤄지는가?: 기후 문제 대응을 위한 공공커뮤니케이션 방향 모색. 광고PR실학연구, 14(3), 155-184.",
    "Pang, B., & Lee, L. (2008). Opinion mining and sentiment analysis. Foundations and Trends in Information Retrieval, 2(1-2), 1-135.",
    "Shapiro, M. A., & Park, H. W. (2018). Climate change and YouTube: Deliberation potential in post-video discussions. Environmental Communication, 12(1), 115-131.",
    "Traag, V. A., Waltman, L., & van Eck, N. J. (2019). From Louvain to Leiden: Guaranteeing well-connected communities. Scientific Reports, 9, 5233.",
]
kor_entries.extend([("body", ref) for ref in kor_refs])


eng_entries = [
    ("title", "Discursive Dynamics of Climate Change in South Korea after the Paris Agreement: A Focus on YouTube Videos, Comments, and Actor Networks"),
    ("author", "Jeonghyeon Park"),
    ("blank", ""),
    ("heading", "1. Introduction"),
    (
        "body",
        "Climate change does not automatically generate social consensus once scientific facts are presented. It is an environmental risk issue whose meaning is continuously renegotiated in public arenas where responsibility, justice, transition costs, and everyday experiences are contested. For that reason, climate discourse should be understood not as a simple distribution of information, but as a socially constructed field in which meanings, emotions, and political alignments are repeatedly reorganized (Beck, 1992; Hilgartner & Bosk, 1988).",
    ),
    (
        "body",
        "This project begins in 2015 because the Paris Agreement established a new institutional reference point for climate politics. At the same time, it distinguishes 2020 as the threshold of a fuller implementation phase. Conceptually, this is the period that the Korean title describes as the “new climate regime”: a post-Paris order shaped by carbon-neutrality agendas, climate-crisis framing, the expanding role of non-state actors, debates over just transition, and the persistent instability of international cooperation. The distinction between 2015 and 2020 therefore matters analytically, because it allows the study to compare a phase of transition and expectation with a phase of implementation, adjustment, and contestation.",
    ),
    (
        "body",
        "On that basis, the study organizes the data in two broad periods, 2015-2019 and 2020-2026, while also comparing major event phases inside each period. These include the 2016 entry into force of the Paris Agreement, the 2017 U.S. withdrawal announcement, the 2021 U.S. re-entry, COP meetings, IPCC assessment outputs, NDC revisions, major climate disasters, and major policy or political events in South Korea. The aim is not merely to identify recurring themes, but to explain how discursive patterns move and are reassembled as political and environmental conditions shift.",
    ),
    (
        "body",
        "YouTube is an especially useful site for this purpose because scientific information, personal experiences, political claims, and distorted climate-related content circulate on the same platform, where video messages can be linked to comment responses (Allgaier, 2019; Shapiro & Park, 2018). Although exposure is shaped by recommendation and personalization, the publicly searchable layer still makes it possible to build a comparatively reproducible longitudinal dataset. This project therefore focuses on Korean-language climate-related YouTube materials that are substantively connected to South Korean channels, audiences, or issues. Prior Korean studies have examined the topic structure and terminology of climate-related YouTube content in South Korea (Lim et al., 2021; Lim, 2023).",
    ),
    ("blank", ""),
    ("heading", "2. Research Objectives"),
    (
        "body",
        "The study aims to explain the discursive dynamics of climate change in South Korea by integrating three analytical layers: expression in videos, reaction in comments, and clustering in actor networks. More specifically, it traces how topics and frames shift over time, how sentiments and attitudes are redistributed across event phases, and how channel-centered networks form, persist, or reorganize. Rather than offering a static description of online discourse, the project seeks to show how the post-Paris climate-governance order is interpreted, contested, and sustained in South Korean public communication.",
    ),
    ("blank", ""),
    ("heading", "3. Research Questions"),
    ("body", "To achieve these objectives, the study addresses the following questions:"),
    (
        "body",
        "RQ1. What topics and frames emerge in South Korean YouTube videos and comments on climate change, and how do they change across the periods 2015-2019 and 2020-2026 as well as around major event phases?",
    ),
    (
        "body",
        "RQ2. How do comment responses vary in sentiment and attitude, and how do acceptance, skepticism, responsibility attribution, policy support or opposition, and delay justification shift across topics and phases?",
    ),
    (
        "body",
        "RQ3. How do commenter-creator networks change over time, which channels or actor clusters become central in particular discursive phases, and what do these shifts suggest about the vulnerabilities and sustaining conditions of climate politics after the Paris Agreement?",
    ),
    ("blank", ""),
    ("heading", "4. Research Methods"),
    (
        "body",
        "The project combines reproducible data collection with descriptive statistics, topic analysis, sentiment and attitude analysis, and actor-network analysis. These components are not treated as separate exercises. Instead, they are read on the same temporal axis so that changes in topics, changes in comment responses, and changes in network configurations can be interpreted together. Depending on corpus size and classification fit, supervised and unsupervised methods will be combined where appropriate.",
    ),
    ("blank", ""),
    ("heading", "4.1 Data Collection"),
    (
        "body",
        "Data will be collected from the publicly searchable area of YouTube through the official YouTube API for the period from December 12, 2015 to January 27, 2026. The units of analysis are videos, channels, comments and replies, and commenter-creator ties. Videos will be organized with titles, descriptions, tags, captions or transcripts, and engagement indicators, while comment data will include text, timestamps, and participation measures. Korean-language content tied to South Korean channels, audiences, or policy contexts will define the operational scope of the corpus.",
    ),
    (
        "body",
        "To improve reproducibility, the project will document collection dates, query terms, sorting conditions, temporal batching rules, responses to result caps, and procedures for missing or unavailable data. Monthly collection will serve as the default strategy, with finer segmentation in periods of heavy volume. The limits of a search-based design, especially its incomplete access to personalized recommendation exposure, will be stated explicitly. Identifiers will be pseudonymized, direct quotation will be minimized, and the need for IRB or equivalent institutional review will be checked before full-scale analysis (Franzke et al., 2020).",
    ),
    ("blank", ""),
    ("heading", "4.2 Topic and Frame Analysis"),
    (
        "body",
        "Topic and frame analysis will be applied to both video texts and comment texts in order to identify major discursive clusters and to compare how their salience changes over time. This step will trace shifts in themes such as climate crisis, carbon neutrality, energy transition, cost burdens, responsibility attribution, and trust in science. Probabilistic topic models and related clustering approaches will be compared, with interpretation guided by representativeness and readability rather than model output alone (Blei et al., 2003). The goal is to show when specific discursive formations become central and how they are reorganized across event phases.",
    ),
    ("blank", ""),
    ("heading", "4.3 Sentiment and Attitude Analysis"),
    (
        "body",
        "Sentiment and attitude analysis will focus primarily on comments. The study distinguishes emotional tones such as anger, anxiety, cynicism, ridicule, and hope from argumentative positions such as scientific acceptance or skepticism, responsibility attribution, policy support or opposition, and delay justification. Dictionary-based methods, supervised classifiers, and manual validation will be combined where useful (Pang & Lee, 2008). This allows the project to examine not only whether specific topics attract attention, but also how they are received and what kinds of response structures intensify or weaken in particular periods.",
    ),
    ("blank", ""),
    ("heading", "4.4 Actor Network Analysis"),
    (
        "body",
        "Actor-network analysis will begin with a bipartite commenter-creator network derived from comment participation. This makes it possible to identify which channels repeatedly attract concentrated responses and which participant clusters are assembled around them. When analytically useful, supplementary indicators such as channel-to-channel connections or co-reference structures in text can also be examined. Centrality measures and community-detection techniques will be used to relate network reconfiguration to topic composition and sentiment-attitude distributions over time (Newman, 2010; Traag et al., 2019).",
    ),
    ("blank", ""),
    ("heading", "5. Expected Outcomes and Implications"),
    (
        "body",
        "Academically, the project will provide an integrated account of topic change, comment response, and actor-network reconfiguration in South Korean climate communication after the Paris Agreement. It extends environmental-sociological concerns with the social construction of risk into a platform-based public arena and offers a way to connect discursive shifts to major political and environmental events. Methodologically, it presents a reproducible design for building and analyzing large-scale YouTube data over time.",
    ),
    (
        "body",
        "Socially and politically, the resulting discourse map can support public communication, media literacy, climate education, and policy discussion by showing which issues, emotions, and actor configurations intensify conflict, justify delay, or enable more constructive engagement. In that sense, the study does not stop at describing discursive patterns. It also provides evidence for assessing the fragilities of climate politics in South Korea and for discussing the communicative conditions under which climate goals can be sustained.",
    ),
    ("blank", ""),
    ("ref_heading", "References"),
]

eng_refs = [
    "Allgaier, J. (2019). Science and environmental communication on YouTube: Strategically distorted communications in online videos on climate change and climate engineering. Frontiers in Communication, 4, 36.",
    "Beck, U. (1992). Risk society: Towards a new modernity. Sage.",
    "Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet Allocation. Journal of Machine Learning Research, 3, 993-1022.",
    "Franzke, A. S., Bechmann, A., Zimmer, M., Ess, C., & Association of Internet Researchers. (2020). Internet research: Ethical guidelines 3.0. Association of Internet Researchers.",
    "Hilgartner, S., & Bosk, C. L. (1988). The rise and fall of social problems: A public arenas model. American Journal of Sociology, 94(1), 53-78.",
    "Newman, M. E. J. (2010). Networks: An introduction. Oxford University Press.",
    "Lim, Y. (2023). Topic modeling of YouTube contents on climate change. Journal of the Korea Convergence Society, 12(2), 139-150.",
    "Lim, Y., Lee, G., & Lee, J. (2021). How are climate change, climate crisis, and global warming addressed on YouTube? Directions for public communication on climate issues. Journal of Practical Research in Advertising and Public Relations, 14(3), 155-184.",
    "Pang, B., & Lee, L. (2008). Opinion mining and sentiment analysis. Foundations and Trends in Information Retrieval, 2(1-2), 1-135.",
    "Shapiro, M. A., & Park, H. W. (2018). Climate change and YouTube: Deliberation potential in post-video discussions. Environmental Communication, 12(1), 115-131.",
    "Traag, V. A., Waltman, L., & van Eck, N. J. (2019). From Louvain to Leiden: Guaranteeing well-connected communities. Scientific Reports, 9, 5233.",
]
eng_entries.extend([("body", ref) for ref in eng_refs])


def main() -> None:
    targets = {
        ROOT / "Doctoral_Research_Plan_5p_KOR.docx": kor_entries,
        ROOT / "Doctoral_Research_Plan_5p_ENG.docx": eng_entries,
    }
    for path in targets:
        backup(path)
    for path, entries in targets.items():
        rewrite(path, entries)
        print(f"rewritten: {path.name}")


if __name__ == "__main__":
    main()

