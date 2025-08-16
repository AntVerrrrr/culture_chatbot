from django.urls import path
from .views import (
    main_view, local_view, chatbot_view, thema_view, independence_view,
    sommelier_view, lounge_view, lounge_chatbot_view, search_results_view,
    memorium_chatbot_view, jp_view,
)

urlpatterns = [
    path("", main_view, name="main-select"),
    path("local/", local_view, name="local-select"),
    path("thema/", thema_view, name="thema-select"),
    path("independence/", independence_view, name="independence-select"),
    path("sommelier/", sommelier_view, name="sommelier-select"),
    path("search/", search_results_view, name="search-results"),
    path("lounge/", lounge_view, name="lounge-select"),
    path("lounge_chatbot/<int:id>/", lounge_chatbot_view, name="chatbot-lounge"),
    path("memorium/<int:id>/", memorium_chatbot_view, name="chatbot-memorium"),
    path("japan/", jp_view, name="jp-select"),           # ← 슬래시 추가
    path("chatbot/<int:id>/", chatbot_view, name="chatbot"),
]
