document.addEventListener('DOMContentLoaded', () => {
    const LANG_KEY = 'preferredLanguage';
    const lang = localStorage.getItem("selectedLanguage") || "ko";
    notifyServerLanguage(lang);

    // 다국어 사전
    const translations = {
        ko: {
            // 설정
            "설정": "설정",
            "내 정보": "내 정보",
            "서비스 이용약관": "서비스 이용약관",
            "서비스 이용약관 상세": "본 서비스의 이용은 다음 약관에 따릅니다. 이용자는 서비스 이용 전 약관을 충분히 숙지해야 하며, 본 서비스를 이용함으로써 약관에 동의한 것으로 간주됩니다.",
            "개인정보 처리방침": "개인정보 처리방침",
            "개인정보 처리방침 상세": "귀하의 개인정보는 관련 법령에 따라 안전하게 보호되며, 서비스 제공 목적 외에는 사용되지 않습니다. 개인정보는 동의 없이 제3자에게 제공되지 않습니다.",
            "청소년 보호정책": "청소년 보호정책",
            "청소년 보호정책 상세": "본 서비스는 청소년 보호를 위해 유해 콘텐츠를 제한하고 있으며, 건전한 인터넷 사용 환경 조성을 위해 노력하고 있습니다. 보호자와 함께 이용을 권장합니다.",
            "다국어 설정": "다국어 설정",

            // 검색창
            "검색창 플레이스홀더": "대화하고 싶은 서비스를 검색해보세요",

            // 카테고리
            "메인": "메인",
            "지역별": "지역별",
            "코레아우라": "코레아우라",
            "소믈리에": "소믈리에",

            //채팅페이지
            "빠른 응답": "빠른 응답",
        },
        en: {
            // 설정
            "설정": "Settings",
            "내 정보": "My Profile",
            "서비스 이용약관": "Terms of Service",
            "서비스 이용약관 상세": "The terms of service apply to this service. Users must fully read them before using, and by using the service, they are deemed to have agreed.",
            "개인정보 처리방침": "Privacy Policy",
            "개인정보 처리방침 상세": "Your personal information is safely protected by law and will not be used for purposes other than service provision. It is not shared with third parties without consent.",
            "청소년 보호정책": "Youth Protection Policy",
            "청소년 보호정책 상세": "This service restricts harmful content to protect youth and promotes a healthy internet environment. Use with parental guidance is recommended.",
            "다국어 설정": "Language Settings",

            // 검색창
            "검색창 플레이스홀더": "Search for the service you want to talk to",

            // 카테고리
            "메인": "Main",
            "지역별": "By Region",
            "코레아우라": "Koreaura",
            "소믈리에": "Sommelier",

            //채팅페이지
            "빠른 응답": "Fast Response",
        },
        ja: {
            // 설정
            "설정": "設定",
            "내 정보": "マイプロフィール",
            "서비스 이용약관": "利用規約",
            "서비스 이용약관 상세": "本サービスの利用には以下の利用規約が適用されます。利用者は利用前に十分に確認する必要があります。",
            "개인정보 처리방침": "個人情報保護方針",
            "개인정보 처리방침 상세": "個人情報は関連法令に従って安全に保護され、目的外使用はされません。",
            "청소년 보호정책": "青少年保護方針",
            "청소년 보호정책 상세": "このサービスは青少年保護のために有害なコンテンツを制限し、健全なインターネット環境を目指しています。",
            "다국어 설정": "言語設定",

            // 검색창
            "검색창 플레이스홀더": "話したいサービスを検索してください",

            // 카테고리
            "메인": "メイン",
            "지역별": "地域別",
            "코레아우라": "コリアオーラ",
            "소믈리에": "ソムリエ",

            //채팅페이지
            "빠른 응답": "高速応答",
        },
        fr: {
            // 설정
            "설정": "Paramètres",
            "내 정보": "Mon profil",
            "서비스 이용약관": "Conditions d'utilisation",
            "서비스 이용약관 상세": "L'utilisation du service est soumise aux conditions suivantes. L'utilisateur est réputé avoir accepté en utilisant le service.",
            "개인정보 처리방침": "Politique de confidentialité",
            "개인정보 처리방침 상세": "Vos informations personnelles sont protégées par la loi et ne seront pas utilisées à d'autres fins.",
            "청소년 보호정책": "Politique de protection des jeunes",
            "청소년 보호정책 상세": "Ce service limite les contenus nuisibles pour protéger les jeunes et favorise un environnement Internet sain.",
            "다국어 설정": "Paramètres linguistiques",

            // 검색창
            "검색창 플레이스홀더": "Recherchez le service avec lequel vous souhaitez discuter",

            // 카테고리
            "메인": "Principal",
            "지역별": "Par région",
            "코레아우라": "Coreaura",
            "소믈리에": "Sommelier",

            //채팅페이지
            "빠른 응답": "Réponse rapide",
        },
        de: {
            // 설정
            "설정": "Einstellungen",
            "내 정보": "Mein Profil",
            "서비스 이용약관": "Nutzungsbedingungen",
            "서비스 이용약관 상세": "Die Nutzung dieses Dienstes unterliegt den folgenden Bedingungen. Mit der Nutzung wird die Zustimmung vorausgesetzt.",
            "개인정보 처리방침": "Datenschutzrichtlinie",
            "개인정보 처리방침 상세": "Ihre persönlichen Daten sind gesetzlich geschützt und werden nicht ohne Zustimmung weitergegeben.",
            "청소년 보호정책": "Jugendschutzrichtlinie",
            "청소년 보호정책 상세": "Dieser Dienst beschränkt schädliche Inhalte zum Schutz der Jugend und fördert ein gesundes Internetumfeld.",
            "다국어 설정": "Spracheinstellungen",

            // 검색창
            "검색창 플레이스홀더": "Suchen Sie den Dienst, mit dem Sie sprechen möchten",

            // 카테고리
            "메인": "Startseite",
            "지역별": "Nach Region",
            "코레아우라": "Coreaura",
            "소믈리에": "Sommelier",

            //채팅페이지
            "빠른 응답": "Schnelle Antwort"
        }
    };

    const select = document.getElementById('languageSelect');

    // 텍스트 업데이트 함수
    function updateTexts(lang) {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (translations[lang] && translations[lang][key]) {
                // input, textarea의 placeholder 처리
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                    el.setAttribute('placeholder', translations[lang][key]);
                } else {
                    el.textContent = translations[lang][key];
                }
            }
        });
    }

    // 서버에 언어 전달 함수 (fetch로 확인용)
    function notifyServerLanguage(langCode) {
        fetch("/api/ping-lang/", {
            method: "GET",
            headers: {
                "X-Language": langCode
            }
        }).then((res) => {
            if (res.ok) console.log("✅ 서버에서 인식한 언어 코드:", langCode);
        });
    }

    // 언어 적용 함수 (UI 반영 + 서버 통신)
    function applyLanguage(lang) {
        localStorage.setItem(LANG_KEY, lang);
        document.cookie = `preferredLanguage=${lang}; path=/;`;
        updateTexts(lang);
        notifyServerLanguage(lang);
    }

    // 로컬스토리지에서 언어 불러오기
    const savedLang = localStorage.getItem(LANG_KEY) || 'ko';
    applyLanguage(savedLang);
    select.value = savedLang;

    // 언어 선택 이벤트 처리
    select.addEventListener('change', (e) => {
        const selectedLang = e.target.value;
//        localStorage.setItem(LANG_KEY, selectedLang);
//        updateTexts(selectedLang);
        applyLanguage(e.target.value);
    });

    // 약관 펼침/접힘 기능
    document.querySelectorAll('.collapsible').forEach(button => {
        button.addEventListener('click', () => {
            const content = button.nextElementSibling;
            const isVisible = content.style.display === 'block';
            content.style.display = isVisible ? 'none' : 'block';
        });
    });

    // 전역에서 호출할 수 있도록 등록
    window.notifyServerLanguage = notifyServerLanguage;
});