from django.urls import path
from . import views
from .views import ping_lang

urlpatterns = [
    path('', views.setting_home, name='setting'),  # /setting/으로 접속 시
    path('ping-lang/', ping_lang, name='ping-lang'),
]