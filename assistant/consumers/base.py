async def connect_to_openai(self):
    import websockets
    import json

    headers = {
        "Authorization": f"Bearer {self.api_key}"
    }

    async with websockets.connect(self.url, extra_headers=headers) as ws:
        self.openai_realtime_websocket = ws

        # 실제 assistant_id, file_ids 포함한 payload 구성
        payload = {
            "type": "start",
            "model": self.model,
            "instructions": self.instructions,
            "tools": [tool.json_schema for tool in self.get_tools()],
        }

        if self.assistant_id:
            payload["assistant_id"] = self.assistant_id
        if self.file_ids:
            payload["file_ids"] = self.file_ids

        await ws.send(json.dumps(payload))

        # 이후 메시지 루프
        await self.agent_loop()