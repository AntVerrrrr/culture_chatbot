# # assistant/management/commands/translate_assistants.py
#
# from django.core.management.base import BaseCommand
# from assistant.models import Assistant
# from django.conf import settings
# from openai import OpenAI
#
# LANGUAGES = ['en', 'ja', 'fr', 'de']
# TRANSLATABLE_FIELDS = [
#     'name',
#     'welcome_message',
#     'question_1', 'question_2', 'question_3', 'question_4', 'question_5',
#     'question_6', 'question_7', 'question_8', 'question_9', 'question_10',
# ]
#
# client = OpenAI(api_key=settings.OPENAI_API_KEY)
#
# def translate_text(text, target_lang):
#     prompt = f"Translate the following Korean text to {target_lang.upper()}:\n\n{text}"
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.3,
#     )
#     return response.choices[0].message.content.strip()
#
# class Command(BaseCommand):
#     help = 'Assistant 모델의 다국어 번역 필드를 자동으로 채웁니다 (원본 필드는 보호됨).'
#
#     def handle(self, *args, **kwargs):
#         assistants = Assistant.objects.all()
#         total_translated = 0
#
#         for assistant in assistants:
#             updated = False
#
#             for field in TRANSLATABLE_FIELDS:
#                 source_value = getattr(assistant, field, None)
#                 if not source_value:
#                     continue  # 원본 데이터가 없는 경우 skip
#
#                 for lang in LANGUAGES:
#                     target_field = f"{field}_{lang}"
#                     target_value = getattr(assistant, target_field, None)
#
#                     if not target_value:
#                         try:
#                             translated = translate_text(source_value, lang)
#                             setattr(assistant, target_field, translated)
#                             self.stdout.write(f"✔ {field} → {target_field} 번역 성공")
#                             total_translated += 1
#                             updated = True
#                         except Exception as e:
#                             self.stderr.write(f"❌ 번역 실패: {field} to {lang} → {e}")
#
#             if updated:
#                 assistant.save()
#
#         self.stdout.write(self.style.SUCCESS(f"🎉 총 {total_translated}개 필드 번역 완료"))