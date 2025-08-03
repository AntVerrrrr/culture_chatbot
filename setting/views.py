from django.shortcuts import render
from django.http import JsonResponse
from django.utils.translation import get_language

def setting_home(request):
    return render(request, 'setting/base_setting.html')

def ping_lang(request):
    # lang = request.headers.get("X-Language", "ko")
    lang = get_language()
    return JsonResponse({"lang": lang})