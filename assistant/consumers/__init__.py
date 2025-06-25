from .base import BaseOpenAIRealtimeConsumer
import urllib.parse

from assistant.utils import get_prompt_context, get_tools_by_assistant

class OpenAIRealtimeConsumer(BaseOpenAIRealtimeConsumer):
    assistant_id: str = ""
    file_ids: list[str] = []
    instructions: str = ""
    tools = []

    async def connect(self):
        query_string = self.scope.get("query_string", b"").decode("utf-8")
        params = urllib.parse.parse_qs(query_string)

        self.assistant_id = params.get("assistant_id", [""])[0]
        file_ids_raw = params.get("file_ids", [""])[0]
        self.file_ids = file_ids_raw.split(",") if file_ids_raw else []

        self.instructions = get_prompt_context(self.assistant_id)
        self.tools = get_tools_by_assistant(self.assistant_id)

        await super().connect()

    async def check_permission(self, user) -> bool:
        return True