from django.contrib import admin
from .models import Assistant, Province, CityCountyTown, Tag
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin   # ✅ 꼭 추가


class TagAdmin(TranslationAdmin):  # ✅ 수정
    list_display = ('name', 'priority')
    search_fields = ('name',)
    list_editable = ('priority',)  # 어드민 페이지에서 우선순위를 직접 수정할 수 있도록 설정

class AssistantAdmin(TranslationAdmin):  # ✅ 수정
    list_display = [
        'name',  # 어시스턴트 이름
        'assistant_id',  # OpenAI assistant id
        'document_id',  # 첨부 문서 ID
        'voice',  # 선택된 음성 (TTS 음성)
        'tag_list',  # 태그 목록 (커스텀 메서드로)
        'welcome_message',  # 간단한 환영 메시지
    ]

    search_fields = ['name', 'assistant_id', 'document_id', 'voice',]
    list_filter = ['country', 'province', 'city_county_town', 'tags', 'voice']
    fields = (
        'name', 'photo', 'assistant_id', 'document_id',
        'country', 'province', 'city_county_town', 'tags',
        'description', 'prompt_context', 'voice',
        'welcome_message',
        'question_1', 'question_2', 'question_3', 'question_4',
        'question_5', 'question_6', 'question_7', 'question_8', 'question_9', 'question_10',
    )
    filter_horizontal = ('tags',)  # ManyToManyField를 쉽게 선택할 수 있도록 필터 사용

    def tag_list(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())

    tag_list.short_description = "태그"


admin.site.register(Assistant, AssistantAdmin)
admin.site.register(Province)
admin.site.register(CityCountyTown)
admin.site.register(Tag, TagAdmin)