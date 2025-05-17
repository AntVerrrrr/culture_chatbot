from django.contrib import admin
from .models import Assistant, Province, CityCountyTown, Tag
from django.utils.html import format_html

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority')
    search_fields = ('name',)
    list_editable = ('priority',)  # 어드민 페이지에서 우선순위를 직접 수정할 수 있도록 설정

class AssistantAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'province', 'city_county_town', 'assistant_id', 'welcome_message']  # assistant_variable은 제거
    search_fields = ['name', 'assistant_id']
    list_filter = ['country', 'province', 'city_county_town', 'tags']
    fields = (
        'assistant_id', 'name', 'photo', 'description', 'country', 'province', 'city_county_town',
        'document_id', 'tags', 'prompt_context',
        'question_1', 'question_2', 'question_3', 'question_4',
        'question_5', 'question_6', 'question_7', 'question_8', 'question_9', 'question_10',
        'welcome_message'
    )
    filter_horizontal = ('tags',)  # ManyToManyField를 쉽게 선택할 수 있도록 필터 사용


admin.site.register(Assistant, AssistantAdmin)
admin.site.register(Province)
admin.site.register(CityCountyTown)
admin.site.register(Tag)