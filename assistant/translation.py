from modeltranslation.translator import register, TranslationOptions
from .models import PageDescription, Province, CityCountyTown, Assistant, Tag

@register(PageDescription)
class PageDescriptionTranslation(TranslationOptions):
    fields = ('text',)

@register(Province)
class ProvinceTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(CityCountyTown)
class CityCountyTownTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Assistant)
class AssistantTranslationOptions(TranslationOptions):
    fields = (
        'name',
        'welcome_message',
        'question_1', 'question_2', 'question_3', 'question_4', 'question_5',
        'question_6', 'question_7', 'question_8', 'question_9', 'question_10',
    )

@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ('name',)