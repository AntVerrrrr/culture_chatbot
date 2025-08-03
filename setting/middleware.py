from django.utils.translation import activate, deactivate

class LanguageHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.headers.get("X-Language") or request.COOKIES.get("preferredLanguage", "ko")
        print(f"🌐 [Middleware] 언어 감지: {lang}")  # ✅ 꼭 추가해봐
        activate(lang)
        request.LANGUAGE_CODE = lang  # modeltranslation 대응
        response = self.get_response(request)
        deactivate()  # 글로벌 상태 초기화
        return response