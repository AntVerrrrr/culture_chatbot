from django.contrib import admin
from .models import Assistant, AssistantLink, Province, CityCountyTown, Tag, PageDescription
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline

@admin.register(PageDescription)
class PageDescriptionAdmin(TranslationAdmin):
    list_display = ('page', 'text', 'order', 'is_active')
    list_filter = ('page', 'is_active')
    search_fields = ('text',)
    ordering = ('page', 'order', 'id')

class TagAdmin(TranslationAdmin):
    list_display = ('name', 'priority')
    search_fields = ('name',)
    list_editable = ('priority',)

class AssistantLinkInline(TranslationTabularInline):
    model = AssistantLink
    extra = 1
    fields = ("title", "url", "order", "is_active", "target_blank")
    ordering = ("order",)

class AssistantAdmin(TranslationAdmin):
    list_display = [
        'id',
        'name',  # 어시스턴트 이름
        'assistant_id',  # OpenAI assistant id
        'document_id',  # 첨부 문서 ID
        'voice',  # 선택된 음성 (TTS 음성)
        # 'tag_list',  # 태그 목록 (커스텀 메서드로)
        # 'welcome_message',  # 간단한 환영 메시지
        # 'greeting',  # 인사말 요약
        # 'link_count',
    ]

    search_fields = ['name', 'assistant_id', 'document_id', 'voice',]
    list_filter = ['country', 'province', 'city_county_town', 'tags', 'voice']
    fields = (
        'name', 'photo', 'assistant_id', 'document_id',
        'country', 'province', 'city_county_town', 'tags',
        'description', 'greeting', 'prompt_context', 'voice',
        'welcome_message',
        'question_1', 'question_2', 'question_3', 'question_4',
        'question_5', 'question_6', 'question_7', 'question_8', 'question_9', 'question_10',
    )
    filter_horizontal = ('tags',)

    inlines = [AssistantLinkInline]

    def tag_list(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())
    tag_list.short_description = "태그"

    def greeting_short(self, obj):
        if not obj.greeting:
            return ""
        s = str(obj.greeting).strip()
        return (s[:20] + "…") if len(s) > 20 else s
    greeting_short.short_description = "인사말"

    def link_count(self, obj):
        return obj.links.count()
    link_count.short_description = "링크 수"

    def tag_list(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())

    tag_list.short_description = "태그"


admin.site.register(Assistant, AssistantAdmin)
admin.site.register(Province)
admin.site.register(CityCountyTown)
admin.site.register(Tag, TagAdmin)