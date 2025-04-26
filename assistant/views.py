from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics
from django.views.decorators.csrf import csrf_exempt
from .models import Province, CityCountyTown, Assistant
from .serializers import ProvinceSerializer, AssistantSerializer, CityCountyTownSerializer
from django.http import StreamingHttpResponse, JsonResponse
import time
from django.utils.timezone import now
import os
from rest_framework.exceptions import ValidationError
from dotenv import load_dotenv
from typing_extensions import override
from openai import OpenAI, AssistantEventHandler
import tempfile
from decouple import config
import re, json, base64
import logging
logger = logging.getLogger(__name__)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from concurrent.futures import ThreadPoolExecutor
#import logging

import redis
from django_redis import get_redis_connection
from django.core.cache import cache
from concurrent.futures import ThreadPoolExecutor
import asyncio
from functools import lru_cache
from django.conf import settings


# -------------------------------------------------------------
# 첫 번째 페이지: 추천 페이지
def main_view(request):
    descriptions = ["다양한 시야로 즐기는 로컬", "역사와 문화를 따라 떠나는 로컬 여행", "로컬 맛집 안에 숨은 이야기"]
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
# 검색 페이지
def search_results_view(request):
    query = request.GET.get('query')
    results = Assistant.objects.filter(name__icontains=query)  # 이름 기준으로 검색
    return render(request, 'search_results.html', {'query': query, 'results': results})

# -------------------------------------------------------------------------------------------------------------------
# 챗봇 페이지 렌더링
def chatbot_view(request, id):
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

    return render(request, 'chatbot.html', {
        'assistant': assistant,
        'id': assistant.id,
        'assistant_id': assistant.assistant_id,
        'document_id': assistant.document_id,
        'assistant_name': assistant.name,
        'questions': questions,
        'welcome_message': assistant.welcome_message
    })




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


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

# -------------------------------------------------------------------------------------------------------------------
# 응답 처리 시 메타데이터 제거
def clean_response(text):
    return re.sub(r'【.*?】', '', text).strip()

class EventHandler(AssistantEventHandler):
    def __init__(self):
        super().__init__()  # 상위 클래스 초기화 호출
        self.responses = []

    @override
    def on_text_created(self, text) -> None:
        # clean_text = clean_response(text.value)  # 'text.value'로 문자열을 추출
        # self.responses.append(clean_text)
        pass

    @override
    def on_message_done(self, message) -> None:
        message_content = message.content[0].text.value  # 'text.value'로 문자열 추출
        clean_text = clean_response(message_content)  # 메타데이터 제거 후 추가
        self.responses.append(clean_text)


#-----------------------------------------------------------------------------------------------------------------------
# .env 파일 로드 (기존 환경 변수 덮어쓰기 허용)
load_dotenv(override=True)

# OpenAI API 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 10,000 원 = 약 $6.9(1$ = 1450원)
# GPT-4o-mini 기준 입력(프롬프트): 1,000 토큰당 $0.01, 출력(응답): 1,000 토큰당 $0.03(1달러면 100,000개 토큰)
# 6.9 * 100,000 = 690,000 토큰 / 한 사람당
# 하루 토큰 제한
TOKEN_LIMIT_PER_DAY = 690000


# Chatbot API (질문을 받아 OpenAI로 처리)
class ChatbotAPIView(APIView):
    def __init__(self):
        super().__init__()
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        try:
            self.redis_connection = get_redis_connection("default")
        except Exception as e:
            self.redis_connection = None

    def get_client_ip(self, request):
        """사용자의 IP 주소 가져오기"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        return ip

    def update_token_usage(self, ip, tokens_used):
        """IP 기반으로 토큰 사용량 업데이트"""
        if not self.redis_connection:
            print("Redis 연결이 없으므로 토큰 사용량을 추적할 수 없습니다.")
            return 0  # Redis가 없으면 사용량을 0으로 처리

        today = now().date()
        cache_key = f"token_usage:{ip}:{today}"
        try:
            used_tokens = self.redis_connection.get(cache_key)
            used_tokens = int(used_tokens) if used_tokens else 0
            new_total = used_tokens + tokens_used
            self.redis_connection.set(cache_key, new_total, ex=86400)  # 24시간 유지
            return new_total
        except Exception as e:
            print(f"Redis 오류: {e}")
            return 0

    def check_token_limit(self, ip, tokens_used):
        """토큰 초과 여부 확인"""
        new_total = self.update_token_usage(ip, tokens_used)

        return new_total > TOKEN_LIMIT_PER_DAY

    def post(self, request, id):
        ip = self.get_client_ip(request)
        assistant = get_object_or_404(Assistant, id=id)
        assistant_id = request.data.get('assistant_id')
        document_id = request.data.get('document_id')
        question = request.data.get('question')
        fast_response = request.data.get('fast_response', False)  # 빠른 응답 모드

        # 토큰 초과 확인
        if self.check_token_limit(ip, 1000):  # 요청당 1000 토큰 가정
            return Response({"error": "Token limit exceeded"}, status=429)

        prompt = f"""
        당신은 '{assistant.name}'입니다.
        - 사람과 대화하듯 답변해주세요.
        - 첨부된 파일의 내용을 바탕으로 답변하세요.
        """

        # 빠른 응답 모드일 경우 프롬프트 추가
        if fast_response:
            prompt += "\n- 답변은 2문장 이내로 요약해서 해주세요."

        # OpenAI API 호출
        response = self.process_chat_request(assistant_id, document_id, question, prompt)

        return Response({"response": response}, status=status.HTTP_200_OK)

    def process_chat_request(self, assistant_id, document_id, question, prompt):
        try:
            thread = client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": question,
                        "attachments": [
                            {"file_id": document_id, "tools": [{"type": "file_search"}]}
                        ]
                    }
                ],
            )

            event_handler = EventHandler()
            with client.beta.threads.runs.stream(
                    thread_id=thread.id,
                    assistant_id=assistant_id,
                    instructions=prompt,
                    event_handler=event_handler,
            ) as stream:
                stream.until_done()

            client.beta.threads.delete(thread.id)

            return event_handler.responses
        except Exception as e:
            return {"error": str(e)}

#-----------------------------------------------------------------------------------------------------------------------
# SST
@csrf_exempt  # CSRF 검사를 예외 처리
def speech_to_text(request):
    if request.method == 'POST':
        if 'audio' not in request.FILES:
            return JsonResponse({'error': 'No audio file provided'}, status=400)
        audio_file = request.FILES['audio']

        # 임시 파일 생성
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')  # with 문 밖에서 생성
        tmp_file_path = tmp_file.name
        try:
            for chunk in audio_file.chunks():
                tmp_file.write(chunk)
            tmp_file.close()  # 파일 쓰기 완료 후 닫기

            # Whisper API 호출
            try:
                with open(tmp_file_path, 'rb') as audio:  # 파일을 다시 열어서 Whisper에 전달
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio,
                        language="ko"
                    )

                # 임시 파일 삭제
                os.unlink(tmp_file_path)
                return JsonResponse({'text': transcript.text})

            except Exception as whisper_e:
                print(f"Whisper API 오류: {whisper_e}")  # 구체적인 예외 메시지 출력
                import traceback
                traceback.print_exc()  # 스택 트레이스 출력
                return JsonResponse({'error': str(whisper_e)}, status=400)  # 에러 반환

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        finally:
            # 에러가 발생하더라도 임시 파일 삭제
            if os.path.exists(tmp_file_path):
                try:
                    os.unlink(tmp_file_path)  # 파일 삭제 시도
                except Exception as unlink_err:
                    print(f"파일 삭제 오류: {unlink_err}")  # 삭제 실패 시 로그

        return JsonResponse({'error': 'Invalid request'}, status=400)
#-----------------------------------------------------------------------------------------------------------------------
# TTS
@csrf_exempt  # CSRF 검사를 예외 처리
def text_to_speech(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text')

            if not text:
                return JsonResponse({'error': 'Text is required'}, status=400)

            # OpenAI TTS API 호출
            response = client.audio.speech.create(
            model="tts-1",
            voice="alloy", # alloy, echo, fable, onyx, nova, shimmer 중 선택
            input=text,
            speed=1.0
            )

            # 오디오 데이터를 base64로 인코딩
            audio_data = base64.b64encode(response.content).decode('utf-8')
            return JsonResponse({'audio_data': audio_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        return JsonResponse({'error': 'Invalid request'}, status=400)
