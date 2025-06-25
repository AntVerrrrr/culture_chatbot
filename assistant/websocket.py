from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from openai import OpenAI
from starlette.websockets import WebSocketState
import os, asyncio, json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

@app.websocket("/ws/start-session/")
async def start_session(websocket: WebSocket):
    await websocket.accept()

    # query 파라미터에서 assistant_id, file_ids 가져오기
    assistant_id = websocket.query_params.get("assistant_id")
    file_ids = websocket.query_params.get("file_ids", "").split(',')

    # 스트리밍 요청용 thread 초기화
    thread = client.beta.threads.create()
    stream = None

    try:
        stream = client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions="듣고 바로 응답하세요.",
            event_handler=None,
            data={"input_audio_format": "webm"}
        )

        await websocket.send_json({"type": "connected", "message": "WebSocket 연결 완료"})

        # 클라이언트에서 음성 데이터를 받아서 OpenAI로 전송
        async for message in websocket.iter_bytes():
            if stream and stream._input_audio_ws and stream._input_audio_ws.client_state == WebSocketState.CONNECTED:
                await stream._input_audio_ws.send_bytes(message)

            if stream and stream._response_ws:
                response_msg = await stream._response_ws.receive_json()
                await websocket.send_json(response_msg)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        if stream:
            await stream.aclose()
        await websocket.close()
        try:
            client.beta.threads.delete(thread.id)
        except:
            pass