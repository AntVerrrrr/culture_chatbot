# assistant/urls.py
from django.urls import path
from .views import (
    main_view,
    local_view,
    chatbot_view,
    thema_view,
    independence_view,
    sommelier_view,
    lounge_view,
    lounge_chatbot_view,
    search_results_view,
    memorium_chatbot_view,
    jp_view,

    AssistantListView,
    ChatbotAPIView,
    speech_to_text,
    text_to_speech,
    )

urlpatterns = [
    path('', main_view, name='main-select'),
    path('local/', local_view, name='local-select'),  # 두 번째 페이지: 지역 선택 후 어시스턴트 연결 페이지
    path('thema/', thema_view, name='thema-select'),
    path('independence/', independence_view, name='independence-select'),
    path('sommelier/', sommelier_view, name='sommelier-select'),
    path('search/', search_results_view, name='search-results'),  # 검색 결과 페이지

    path('lounge/', lounge_view, name='lounge-select'),  # 라운지페이지
    path('lounge_chatbot/<int:id>/', lounge_chatbot_view, name='chatbot-lounge'),

    path('memorium/<int:id>/', memorium_chatbot_view, name='chatbot-memorium'),

    path('jp', jp_view, name='jp-select'),  # 라운지페이지

    path('chatbot/<int:id>/', chatbot_view, name='chatbot'),

    path('api/assistants/', AssistantListView.as_view(), name='assistant-list'),
    path("api/chatbot/<int:id>/", ChatbotAPIView.as_view(), name="chatbot"),

    path('stt/', speech_to_text, name='speech_to_text'),
    path('tts/', text_to_speech, name='text_to_speech'),
]
