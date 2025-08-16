# culture_chatbot/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog

# 🔌 API: i18n 영향 X (항상 고정)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),  # Django 표준 i18n 엔드포인트
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("api/assistant/", include("assistant.api_urls")),
]

# 🌐 페이지: i18n 적용
urlpatterns += i18n_patterns(
    path("", include("assistant.urls")),
    path("setting/", include("setting.urls")),
    prefix_default_language=False,
)

# 정적/미디어: 개발 환경에서만 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # 필요하면 정적파일도:
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)






