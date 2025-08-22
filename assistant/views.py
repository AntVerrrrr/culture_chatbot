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
from .models import Province, CityCountyTown, Assistant, PageDescription
from .serializers import ProvinceSerializer, AssistantSerializer, CityCountyTownSerializer

import tempfile, os, json, base64, logging, re, openai
from django.utils import translation
from django.utils.translation import activate
from django.utils.translation import get_language

logger = logging.getLogger(__name__)
load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TOKEN_LIMIT_PER_DAY = 690000

# -----------------------------------------------------------------------------------------------------------------
# 첫 번째 페이지: 추천 페이지
def main_view(request):
    lang = (get_language() or 'ko')[:2]

    rows = PageDescription.objects.filter(page='main', is_active=True).order_by('order', 'id')
    assistants_by_description = {}

    for row in rows:
        # 화면에 보여줄 언어별 텍스트
        label = (getattr(row, f'text_{lang}', None)
                 or row.text_ko
                 or row.text)

        # Assistant 필터는 항상 한국어 기준으로
        assistants = Assistant.objects.filter(description=row.text_ko)

        assistants_by_description[label] = assistants

    return render(request, 'assistant/assistants_pages/main.html', {
        'assistants_by_description': assistants_by_description
    })

# -----------------------------------------------------------------------------------------------------------------
def local_view(request):
    provinces = Province.objects.prefetch_related('cities').order_by('id')
    return render(request, 'assistant/assistants_pages/local.html', {'provinces': provinces})

def AssistantListView(request):
    province_id = request.GET.get('province_id')
    city_id = request.GET.get('city_id')

    qs = Assistant.objects.all()
    if province_id:
        qs = qs.filter(province_id=province_id)
    if city_id:
        qs = qs.filter(city_county_town_id=city_id)

    lang = (request.GET.get('lang') or get_language() or 'ko')[:2]
    activate(lang)
    name_field = f'name_{lang}'
    tag_field = f'name_{lang}'

    data = []
    for a in qs.select_related('province','city_county_town').prefetch_related('tags'):
        # Assistant 이름
        localized_name = getattr(a, name_field, None) or a.name
        # 태그 이름들
        tags = [
            {
                "name": (getattr(t, tag_field, None) or t.name),
                "priority": t.priority
            }
            for t in a.tags.all()
        ]

        data.append({
            "id": a.id,
            "name": localized_name,
            "photo": a.photo.url,
            "tags": tags,
        })

    return JsonResponse(data, safe=False)
# -------------------------------------------------------------------------------------------------------------------
# 숨겨진 페이지
def thema_view(request):
    return render(request, 'assistant/assistants_pages/thema.html')

# -------------------------------------------------------------------------------------------------------------------
# 세 번째 페이지: 독립 선택 페이지
def independence_view(request):
    lang = (get_language() or 'ko')[:2]

    rows = (
        PageDescription.objects
        .filter(page='koreaura', is_active=True)
        .order_by('order', 'id')
    )

    assistants_by_description = {}
    for row in rows:
        # 화면 표시는 현재 언어(없으면 ko → 원문 순)
        label = getattr(row, f'text_{lang}', None) or row.text_ko or row.text
        # 매칭은 한국어 텍스트(없으면 원문)로 필터
        ko_key = row.text_ko or row.text
        assistants = (
            Assistant.objects
            .filter(description=ko_key)
            .prefetch_related('tags')
        )
        assistants_by_description[label] = assistants

    return render(
        request,
        'assistant/assistants_pages/independence.html',
        {'assistants_by_description': assistants_by_description}
    )
# -------------------------------------------------------------------------------------------------------------------
# 네 번째 페이지: 지역 상인 페이지
def sommelier_view(request):
    lang = (get_language() or 'ko')[:2]

    rows = (
        PageDescription.objects
        .filter(page='sommelier', is_active=True)
        .order_by('order', 'id')
    )

    assistants_by_description = {}
    for row in rows:
        # 화면에 표시할 텍스트 (현재 언어 → ko → 기본 text 순)
        label = getattr(row, f'text_{lang}', None) or row.text_ko or row.text
        # 한국어 기준으로 Assistant 매칭
        ko_key = row.text_ko or row.text
        assistants = (
            Assistant.objects
            .filter(description=ko_key)
            .prefetch_related('tags')
        )
        assistants_by_description[label] = assistants

    return render(
        request,
        'assistant/assistants_pages/sommelier.html',
        {'assistants_by_description': assistants_by_description}
    )
# -------------------------------------------------------------------------------------------------------------------
# 검색 페이지
def search_results_view(request):
    query = request.GET.get('query')
    results = Assistant.objects.filter(name__icontains=query)  # 이름 기준으로 검색
    return render(request, 'assistant/assistants_pages/search_results.html', {'query': query, 'results': results})

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

    return render(request, 'assistant/chatbot_pages/chatbot.html', {
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
        print("📩 on_message_done 호출됨")
        print("📦 message.content:", message.content)

        try:
            text = message.content[0].text.value
            print("📝 원본 응답:", text)
        except Exception as e:
            print("❌ 응답 파싱 실패:", e)
            return

        text = re.sub(r'【.*?】', '', text)  # 괄호 주석 제거
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # **강조** 제거
        clean = text.strip()

        print("✅ 정리된 응답:", clean)
        self.responses.append(clean)

        if hasattr(message, 'usage') and message.usage and message.usage.total_tokens:
            self.usage = message.usage.total_tokens
            print("🔢 사용된 토큰 수:", self.usage)


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
        use_file_search = bool(request.data.get('file_search'))

        print("❓ question:", question)
        print("📄 document_id:", assistant.document_id)
        print("🤖 assistant_id:", assistant.assistant_id)
        # print("⚡ fast_response:", fast_response)
        print("🔎 file_search:", use_file_search)
        # prompt = assistant.prompt_context or f"당신은 '{assistant.name}'입니다.\n- 첨부된 파일의 내용을 바탕으로 대답해주세요."
        # if str(fast_response).lower() == "true":
        #     prompt += "\n- 답변은 2문장 이내로 간결하게 요약해주세요."

        # 파일서치 문구는 켰을 때만 안내(선택)
        if use_file_search:
            prompt = (assistant.prompt_context or f"당신은 '{assistant.name}'입니다.") + \
                     "\n- 가능한 경우 첨부 파일(벡터 검색) 내용을 근거로 답변하세요."
        else:
            prompt = assistant.prompt_context or f"당신은 '{assistant.name}'입니다."
        print("📢 prompt_context:", prompt)

        try:
            # thread = client.beta.threads.create(messages=[{
            #     "role": "user", "content": question,
            #     "attachments": [{"file_id": assistant.document_id, "tools": [{"type": "file_search"}]}]
            # }])
            # print("🧵 thread 생성:", thread.id)

            # ✅ file_search ON일 때만 첨부+툴 포함
            user_msg = {"role": "user", "content": question}
            if use_file_search and assistant.document_id:
                user_msg["attachments"] = [{
                    "file_id": assistant.document_id,
                    "tools": [{"type": "file_search"}]
                }]
            thread = client.beta.threads.create(messages=[user_msg])
            print("🧵 thread 생성:", thread.id)

            handler = EventHandler()
            with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant.assistant_id,
                instructions=prompt,
                event_handler=handler
            ) as stream:
                stream.until_done()
            print("✅ stream 완료")

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
        data = json.loads(request.body)
        text = data.get('text')
        assistant_db_id = data.get('id')

        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)

        # response = client.audio.speech.create(
        #     model="tts-1", voice="nova", input=text, speed=1.0)

        # DB에서 voice 값 가져오기

        try:
            assistant = Assistant.objects.get(id=assistant_db_id)
            voice = (assistant.voice or 'nova').lower()
        except Assistant.DoesNotExist:
            voice = 'nova'

        # print(f"[DEBUG] text: {text}")
        print(f"[DEBUG] id: {assistant_db_id}")
        print(f"[DEBUG] selected voice: {voice}")

        # OpenAI TTS 요청
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            speed=1.0
        )

        audio_data = base64.b64encode(response.content).decode('utf-8')
        return JsonResponse({'audio_data': audio_data})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# -------------------------------------------------------------------------------------------------------------------
def debug_lang_view(request):
    activate('ja')
    assistant = Assistant.objects.first()

    print("🌐 LANGUAGE_CODE--:", get_language())
    print("🟡 name_ja--:", assistant.name_ja)
    print("🔵 assistant.--:", assistant.name)
    return JsonResponse({'name': assistant.name})




