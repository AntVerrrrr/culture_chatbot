from django.urls import path
from . import views

urlpatterns = [
    path("", views.setting_home, name="setting"),  # 빈 경로여야 /<lang>/setting/과 매칭됨
]