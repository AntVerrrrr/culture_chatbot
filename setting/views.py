from django.shortcuts import render
from django.http import JsonResponse
from django.utils.translation import get_language

def setting_home(request):
    return render(request, 'setting/base_setting.html')

