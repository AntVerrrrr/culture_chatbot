from django.urls import path
from .views import AssistantListView, ChatbotAPIView, speech_to_text, text_to_speech

urlpatterns = [
    path("list/", AssistantListView, name="assistant-list"),
    path("chatbot/<int:id>/", ChatbotAPIView.as_view(), name="chatbot"),  # ← 파일서치 포함
    path("stt/", speech_to_text, name="speech-to-text"),
    path("tts/", text_to_speech, name="text-to-speech"),
]