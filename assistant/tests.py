import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY") or "sk-..."  # 키가 있으면 대체

try:
    session = openai.beta.assistants.realtime.sessions.create(
        assistant_id="asst_QdqM7VVU8LtjH94OtSKMQTg0"
    )
    print("✅ 생성 완료:", session.id)
except Exception as e:
    print("🔥 오류:", str(e))