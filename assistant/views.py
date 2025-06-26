from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from django_redis import get_redis_connection
from django.utils.timezone import now
from dotenv import load_dotenv
from decouple import config
from typing_extensions import override
from openai import OpenAI, AssistantEventHandler
from .models import Province, CityCountyTown, Assistant
from .serializers import ProvinceSerializer, AssistantSerializer, CityCountyTownSerializer

import tempfile, os, json, base64, logging, re, openai

logger = logging.getLogger(__name__)
load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TOKEN_LIMIT_PER_DAY = 690000

# -------------------------------------------------------------
# 첫 번째 페이지: 추천 페이지
def main_view(request):
    descriptions = ["로컬 크리에이터와 나누는 대화", "로컬 캐릭터와 즐기는 대화", "소주어리: 안동소주 투어", "코레아우라! 독립운동을 따라 즐기는 안동"]
    assistants_by_description = {}

    # 각 description에 맞는 어시스턴트 데이터를 가져옴
    for description in descriptions:
        assistants_by_description[description] = Assistant.objects.filter(description=description)

    return render(request, 'main.html', {'assistants_by_description': assistants_by_description})

# -------------------------------------------------------------
# 두 번째 페이지: 지역 선택 페이지
def local_view(request):
    return render(request, 'local.html')

# 도 목록 API
class ProvinceListView(generics.ListAPIView):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer

# 시/군/읍 목록 API
class CityCountyTownListView(generics.ListAPIView):
    serializer_class = CityCountyTownSerializer

    def get_queryset(self):
        province_name = self.request.query_params.get('province')
        if province_name:
            return CityCountyTown.objects.filter(province__name=province_name)
        return CityCountyTown.objects.none()

# 어시스턴트 목록 API
class AssistantListView(generics.ListAPIView):
    serializer_class = AssistantSerializer

    def get_queryset(self):
        province_name = self.request.query_params.get('province')
        city_name = self.request.query_params.get('city_county_town')
        if province_name and city_name:
            return Assistant.objects.filter(city_county_town__name=city_name, city_county_town__province__name=province_name)
        return Assistant.objects.none()
# -------------------------------------------------------------------------------------------------------------------
# 숨겨진 페이지
def thema_view(request):
    return render(request, 'thema.html')

# -------------------------------------------------------------------------------------------------------------------
# 세 번째 페이지: 독립 선택 페이지
def independence_view(request):
    descriptions = ["보드게임 룰이 궁금하시나요?", "문학으로 아픔을 풀어낸 독립운동가", "전장을 누볐던 무장 독립투사", "항일의 빛, 계몽의 사자"]
    assistants_by_description = {}

    # 각 description에 맞는 어시스턴트 데이터를 가져옴
    for description in descriptions:
        assistants_by_description[description] = Assistant.objects.filter(description=description)

    return render(request, 'independence.html', {'assistants_by_description': assistants_by_description})

# -------------------------------------------------------------------------------------------------------------------
# 네 번째 페이지: 지역 상인 페이지
def sommelier_view(request):
    descriptions = ["트랜디한 전통주 와이너리", "막걸리로 즐기는 전통주", "역사가 담긴 한 잔, 안동소주", "파티와 함께하는 이색 전통주"]
    assistants_by_description = {}

    # 각 description에 맞는 어시스턴트 데이터를 갖옴
    for description in descriptions:
        assistants_by_description[description] = Assistant.objects.filter(description=description)

    return render(request, 'sommelier.html', {'assistants_by_description': assistants_by_description})

# -------------------------------------------------------------------------------------------------------------------
# 다섯 번째 페이지: 라운지 페이지
def lounge_view(request):
    descriptions = ["Hahoe Village, curved like a lotus flower", "Dosanseowon, a place of Joseon wisdom", "Byeongsan Seowon, like a beautiful folding screen", "Sad love in the moonlight", "Enjoy a fun round of mask dance in Andong"]
    assistants_by_description = {}

    # 각 description에 맞는 어시스턴트 데이터를 갖옴
    for description in descriptions:
        assistants_by_description[description] = Assistant.objects.filter(description=description)

    return render(request, 'lounge.html', {'assistants_by_description': assistants_by_description})

# -------------------------------------------------------------------------------------------------------------------
# 여섯 번째 페이지: 일본 박람회 준비
def jp_view(request):
    descriptions = ["ローカルクリエイターとの対話", "ローカルキャラクターと楽しむ会話", "沖縄泡盛ツアー", "東京日本酒ツアー"]
    assistants_by_description = {}

    # 각 description에 맞는 어시스턴트 데이터를 가져옴
    for description in descriptions:
        assistants_by_description[description] = Assistant.objects.filter(description=description)

    return render(request, 'japan.html', {'assistants_by_description': assistants_by_description})

# -------------------------------------------------------------------------------------------------------------------
# 검색 페이지
def search_results_view(request):
    query = request.GET.get('query')
    results = Assistant.objects.filter(name__icontains=query)  # 이름 기준으로 검색
    return render(request, 'search_results.html', {'query': query, 'results': results})

### ---------- 일반 렌더링 뷰 ---------- ###
def chatbot_view(request, id):
    request.session.pop('thread_id', None)
    assistant = get_object_or_404(Assistant, id=id)
    questions = [q for q in [
        assistant.question_1, assistant.question_2, assistant.question_3,
        assistant.question_4, assistant.question_5, assistant.question_6,
        assistant.question_7, assistant.question_8, assistant.question_9,
        assistant.question_10
    ] if q]

    return render(request, 'chatbot.html', {
        'assistant': assistant,
        'id': assistant.id,
        'assistant_id': assistant.assistant_id,
        'document_id': assistant.document_id,
        'assistant_name': assistant.name,
        'questions': questions,
        'welcome_message': assistant.welcome_message
    })


def voice_chat_view(request):
    assistant_id = request.GET.get("assistant_id", "")
    file_ids = request.GET.getlist("file_ids")
    return render(request, "chatbot.html", {
        "assistant_id": assistant_id,
        "file_ids": file_ids
    })


### ---------- 챗봇 API (POST 텍스트 질문 처리) ---------- ###
class EventHandler(AssistantEventHandler):
    def __init__(self):
        super().__init__()
        self.responses = []
        self.usage = 0

    def on_message_done(self, message) -> None:
        clean = re.sub(r'【.*?】', '', message.content[0].text.value).strip()
        self.responses.append(clean)
        if hasattr(message, 'usage') and message.usage and message.usage.total_tokens:
            self.usage = message.usage.total_tokens


class ChatbotAPIView(APIView):
    def __init__(self):
        super().__init__()
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        try:
            self.redis = get_redis_connection("default")
        except:
            self.redis = None

    def get_client_ip(self, request):
        return request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')).split(',')[0]

    def update_token_usage(self, ip, used):
        if not self.redis:
            return 0
        key = f"token_usage:{ip}:{now().date()}"
        total = int(self.redis.get(key) or 0) + used
        self.redis.set(key, total, ex=86400)
        return total

    def check_token_limit(self, ip):
        if not self.redis:
            return False
        key = f"token_usage:{ip}:{now().date()}"
        return int(self.redis.get(key) or 0) > TOKEN_LIMIT_PER_DAY

    def post(self, request, id):
        ip = self.get_client_ip(request)
        assistant = get_object_or_404(Assistant, id=id)
        question = request.data.get('question')
        fast_response = request.data.get('fast_response')

        print("❓ question:", question)
        print("📄 document_id:", assistant.document_id)
        print("🤖 assistant_id:", assistant.assistant_id)
        print("⚡ fast_response:", fast_response)
        prompt = assistant.prompt_context or f"당신은 '{assistant.name}'입니다.\n- 첨부된 파일의 내용을 바탕으로 대답해주세요."
        if str(fast_response).lower() == "true":
            prompt += "\n- 답변은 2문장 이내로 간결하게 요약해주세요."

        try:
            thread = client.beta.threads.create(messages=[{
                "role": "user", "content": question,
                "attachments": [{"file_id": assistant.document_id, "tools": [{"type": "file_search"}]}]
            }])

            handler = EventHandler()
            with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant.assistant_id,
                instructions=prompt,
                event_handler=handler
            ) as stream:
                stream.until_done()

            self.update_token_usage(ip, handler.usage)
            if self.check_token_limit(ip):
                return Response({"error": "Token limit exceeded"}, status=429)

            return Response({"response": handler.responses}, status=200)
        except Exception as e:
            logger.exception("OpenAI 처리 중 오류")
            return Response({"error": str(e)}, status=500)
        finally:
            try:
                client.beta.threads.delete(thread.id)
            except:
                pass

### ---------- Whisper STT ---------- ###
@csrf_exempt
def speech_to_text(request):
    if request.method != 'POST' or 'audio' not in request.FILES:
        return JsonResponse({'error': 'Audio file required'}, status=400)

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
    for chunk in request.FILES['audio'].chunks():
        tmp_file.write(chunk)
    tmp_file.close()

    try:
        with open(tmp_file.name, 'rb') as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", file=audio, language="ko")
        return JsonResponse({'text': transcript.text})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    finally:
        os.unlink(tmp_file.name)


### ---------- OpenAI TTS ---------- ###
@csrf_exempt
def text_to_speech(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        text = json.loads(request.body).get('text')
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)

        response = client.audio.speech.create(
            model="tts-1", voice="nova", input=text, speed=1.0)
        audio_data = base64.b64encode(response.content).decode('utf-8')
        return JsonResponse({'audio_data': audio_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# -------------------------------------------------------------------------------------------------------------------
# 라운지 챗봇 페이지 렌더링
def lounge_chatbot_view(request, id):
    # 새로운 어시스턴트로 이동할 때 세션에서 스레드 ID 삭제
    request.session.pop('thread_id', None)

    assistant = get_object_or_404(Assistant, id=id)

    # 질문을 리스트로 준비
    questions = [
        assistant.question_1,
        assistant.question_2,
        assistant.question_3,
        assistant.question_4,
        assistant.question_5,
        assistant.question_6,
        assistant.question_7,
        assistant.question_8,
        assistant.question_9,
        assistant.question_10,
    ]

    questions = [q for q in questions if q]  # None 값 제외

    return render(request, 'lounge_chatbot.html', {
        'assistant': assistant,
        'id': assistant.id,
        'assistant_id': assistant.assistant_id,
        'document_id': assistant.document_id,
        'assistant_name': assistant.name,
        'questions': questions,
        'welcome_message': assistant.welcome_message
    })


# -------------------------------------------------------------------------------------------------------------------
# 메모리움 챗봇 페이지 렌더링
def memorium_chatbot_view(request, id):
    # 새로운 어시스턴트로 이동할 때 세션에서 스레드 ID 삭제
    request.session.pop('thread_id', None)

    assistant = get_object_or_404(Assistant, id=id)

    # 질문을 리스트로 준비
    questions = [
        assistant.question_1,
        assistant.question_2,
        assistant.question_3,
        assistant.question_4,
        assistant.question_5,
        assistant.question_6,
        assistant.question_7,
        assistant.question_8,
        assistant.question_9,
        assistant.question_10,
    ]

    questions = [q for q in questions if q]  # None 값 제외

    return render(request, 'memorium_chatbot.html', {
        'assistant': assistant,
        'id': assistant.id,
        'assistant_id': assistant.assistant_id,
        'document_id': assistant.document_id,
        'assistant_name': assistant.name,
        'questions': questions,
        'welcome_message': assistant.welcome_message
    })




