from django.db import models

class Province(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CityCountyTown(models.Model):
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return f"{self.province.name} - {self.name}"

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    priority = models.IntegerField(default=0)  # 우선순위를 저장하는 필드 추가

    def __str__(self):
        return self.name


class Assistant(models.Model):
    name = models.CharField(max_length=255)  # 어시스턴트 이름
    photo = models.ImageField(
        upload_to='assistant_photos/',
        null=False,
        blank=False,
        default='assistant_photos/default.png'  # 기본 이미지 설정
    ) # 어시스턴트 이미지
    assistant_id = models.CharField(max_length=255, unique=True, null=False, default='default_assistant_id')  # 어시스턴트 아이디
    document_id = models.CharField(max_length=255, null=True, blank=True)  # 문서 ID를 저장하는 필드


    country = models.CharField(max_length=100, default='대한민국')  # 나라
    province = models.ForeignKey('Province', on_delete=models.CASCADE,default=1)  # 기본값으로 ID 1인 Province 사용 경상북도, 경상남도 등등
    city_county_town = models.ForeignKey('CityCountyTown', on_delete=models.CASCADE)  # 시군읍 정보
    tags = models.ManyToManyField(Tag, related_name='assistants', blank=True)  # 어시스턴트 해시태그


    description = models.TextField(default='No description available')  # 어시스턴트 설명
    # 어시스턴트 성격 설정
    prompt_context = models.TextField(
        blank=True,
        null=True,
        help_text="이 Assistant가 따르는 기본 프롬프트를 적어주세요 (말투/성격/역할 등)"
    )
    # 어시스턴트 보이스
    voice = models.CharField(
        max_length=50,
        choices=[
            ('nova', 'Nova'),
            ('shimmer', 'Shimmer'),
            ('echo', 'Echo'),
            ('onyx', 'Onyx'),
            ('fable', 'Fable'),
        ],
        default='nova',
        help_text='TTS 음성 선택 (OpenAI에서 지원하는 음성 이름)'
    )


    # welcome message
    welcome_message = models.TextField(default='환영합니다! 무엇을 도와드릴까요?')  # Store a single welcome message


    # 질문 필드 추가
    question_1 = models.TextField(null=True, blank=True)
    question_2 = models.TextField(null=True, blank=True)
    question_3 = models.TextField(null=True, blank=True)
    question_4 = models.TextField(null=True, blank=True)
    question_5 = models.TextField(null=True, blank=True)
    question_6 = models.TextField(null=True, blank=True)
    question_7 = models.TextField(null=True, blank=True)
    question_8 = models.TextField(null=True, blank=True)
    question_9 = models.TextField(null=True, blank=True)
    question_10 = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.name
