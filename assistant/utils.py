from assistant.models import Assistant

def get_prompt_context(assistant_id: str) -> str:
    try:
        assistant = Assistant.objects.get(assistant_id=assistant_id)
        return assistant.prompt_context
    except Assistant.DoesNotExist:
        return "You are a helpful assistant. Speak Korean."

def get_tools_by_assistant(assistant_id: str):
    # 필요 시 어시스턴트별 도구 지정 가능
    from langchain_community.tools import TavilySearchResults

    tavily_tool = TavilySearchResults(
        max_results=5,
        include_answer=True,
        description=(
            "This is a search tool for accessing the internet.\n\n"
            "Let the user know you're asking your friend Tavily for help before you call the tool."
        )
    )
    return [tavily_tool]