// static/js/i18n/i18n.js

document.addEventListener('DOMContentLoaded', () => {
    const translations = {
        ko: {
            "설정": "설정",
            "검색 문구": "대화하고 싶은 서비스를 검색해보세요"
        },
        en: {
            "설정": "Settings",
            "검색 문구": "Search for the service you want to talk to"
        },
        ja: {
            "설정": "設定",
            "검색 문구": "会話したいサービスを検索してください"
        },
        fr: {
            "설정": "Paramètres",
            "검색 문구": "Recherchez le service avec lequel vous souhaitez discuter"
        },
        de: {
            "설정": "Einstellungen",
            "검색 문구": "Suchen Sie nach dem gewünschten Service"
        }
    };

    const lang = localStorage.getItem('lang') || 'ko';

    function updateTexts(lang) {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (translations[lang] && translations[lang][key]) {
                el.textContent = translations[lang][key];
            }
        });

        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (translations[lang] && translations[lang][key]) {
                el.placeholder = translations[lang][key];
            }
        });
    }

    updateTexts(lang);

    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect) {
        languageSelect.value = lang;
        languageSelect.addEventListener('change', (e) => {
            const selectedLang = e.target.value;
            localStorage.setItem('lang', selectedLang);
            updateTexts(selectedLang);
        });
    }
});