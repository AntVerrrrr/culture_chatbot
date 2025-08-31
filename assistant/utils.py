from typing import List, Dict, Iterable, Optional
from django.db.models import QuerySet
from .models import Assistant, PageDescription, Tag


def build_sections_by_pagedescription(
    page_key: str,
    include_empty_sections: bool = True,
    assistant_ordering: Iterable[str] = ("id",),
) -> List[Dict]:
    """
    일반 페이지용.
    PageDescription(page=page_key, is_active=True)를 order 순서대로 읽어
    '표시는 현재 언어(row.text)', '매칭은 항상 한국어(row.text_ko)'로 수행.
    """
    rows = (
        PageDescription.objects
        .filter(page=page_key, is_active=True)
        .order_by("order", "id")
    )

    sections: List[Dict] = []
    for row in rows:
        # 화면 표시는 modeltranslation이 현재 언어로 매핑된 값
        label = row.text

        # 매칭 키는 항상 한국어 기준 (없으면 최후에 row.text로 fallback)
        ko_key = getattr(row, "text_ko", None) or row.text

        assistants = (
            Assistant.objects
            .filter(description__iexact=ko_key)   # 대소문자/공백 미세차 완화
            .prefetch_related("tags")
            .order_by(*assistant_ordering)
        )

        if assistants.exists() or include_empty_sections:
            sections.append({"label": label, "assistants": assistants})

    return sections


def build_sections_by_top_tag_of_assistant(
    assistant: Assistant,
    limit: int = 20,
    exclude_self: bool = True,
    ordering: Iterable[str] = ("id",),
) -> List[Dict]:
    """
    프리뷰 페이지용.
    해당 assistant의 태그 중 priority가 가장 큰 Tag 하나를 골라,
    그 태그를 공유하는 Assistant들을 한 섹션으로 반환.

    반환 포맷:
      [
        {"label": f"#{tag.name} 추천", "assistants": QuerySet[Assistant]},
      ]
    """
    top_tag: Optional[Tag] = assistant.tags.all().order_by("-priority", "id").first()
    if not top_tag:
        return []

    qs: QuerySet[Assistant] = (
        Assistant.objects
        .filter(tags=top_tag)
        .prefetch_related("tags")
        .order_by(*ordering)
    )
    if exclude_self:
        qs = qs.exclude(id=assistant.id)
    if limit:
        qs = qs[:limit]

    # modeltranslation 덕분에 tag.name 만 써도 현재 언어로 표시됨
    # label = f"#{top_tag.name} 추천"
    return [{"assistants": qs}]






# from assistant.models import Assistant
#
# def get_prompt_context(assistant_id: str) -> str:
#     try:
#         assistant = Assistant.objects.get(assistant_id=assistant_id)
#         return assistant.prompt_context
#     except Assistant.DoesNotExist:
#         return "You are a helpful assistant. Speak Korean."
#
# def get_tools_by_assistant(assistant_id: str):
#     # 필요 시 어시스턴트별 도구 지정 가능
#     from langchain_community.tools import TavilySearchResults
#
#     tavily_tool = TavilySearchResults(
#         max_results=5,
#         include_answer=True,
#         description=(
#             "This is a search tool for accessing the internet.\n\n"
#             "Let the user know you're asking your friend Tavily for help before you call the tool."
#         )
#     )
#     return [tavily_tool]