//// i18n-helper.js
//// 번역 함수의 폴백 정의
//// Django의 gettext 계열 함수들이 로드되지 않았을 경우를 대비한 처리
//
//export const _ = (typeof gettext === "function") ? gettext : (s) => s;
//export const _n = (typeof ngettext === "function") ? ngettext : (s1, s2, c) => (c === 1 ? s1 : s2);
//export const _p = (typeof pgettext === "function") ? pgettext : (_ctx, s) => s;


// static/js/i18n-helper.js

// --- URL 프리픽스(/en|ja|fr|de)에서 언어 결정 (없으면 ko) ---
function detectLocaleFromUrl() {
  const m = location.pathname.match(/^\/(en|ja|fr|de)(?=\/|$)/i);
  return m ? m[1].toLowerCase() : "ko";
}
const CURRENT_LOCALE = detectLocaleFromUrl();

// --- 경량 사전(필요 키만) ---
const DICT = {
  ko: {
    "생각 중": "생각 중",
    "듣는 중...": "듣는 중...",
    "마이크 접근에 실패했습니다.": "마이크 접근에 실패했습니다."
  },
  en: {
    "생각 중": "Thinking",
    "듣는 중...": "Listening...",
    "마이크 접근에 실패했습니다.": "Failed to access microphone."
  },
  ja: {
    "생각 중": "考え中",
    "듣는 중...": "聞いています...",
    "마이크 접근에 실패했습니다.": "マイクへのアクセスに失敗しました。"
  },
  fr: {
    "생각 중": "Réflexion en cours",
    "듣는 중...": "En écoute...",
    "마이크 접근에 실패했습니다.": "Échec d'accès au microphone."
  },
  de: {
    "생각 중": "Am Nachdenken",
    "듣는 중...": "Hört zu...",
    "마이크 접근에 실패했습니다.": "Zugriff auf Mikrofon fehlgeschlagen."
  }
};

// --- Django gettext 계열이 있으면 우선 사용(없어도 에러 안 나게 안전 체크) ---
const hasWindow = typeof window !== "undefined";
const hasGettext  = hasWindow && typeof window.gettext  === "function";
const hasNGettext = hasWindow && typeof window.ngettext === "function";
const hasPGettext = hasWindow && typeof window.pgettext === "function";

// --- 단건 번역 ---
export const _ = (s) => {
  if (hasGettext) return window.gettext(s);
  const table = DICT[CURRENT_LOCALE] || {};
  return table[s] || s;
};

// --- 복수형 번역 (폴백: 1이면 단수, 아니면 복수) ---
export const _n = (s1, s2, count) => {
  if (hasNGettext) return window.ngettext(s1, s2, count);
  return count === 1 ? s1 : s2;
};

// --- 컨텍스트 번역 (폴백: 컨텍스트 무시) ---
export const _p = (ctx, s) => {
  if (hasPGettext) return window.pgettext(ctx, s);
  const table = DICT[CURRENT_LOCALE] || {};
  return table[s] || s;
};

// --- 유틸(선택) ---
export function getLocale() {
  return CURRENT_LOCALE;
}
export function addTranslations(locale, entries) {
  if (!DICT[locale]) DICT[locale] = {};
  Object.assign(DICT[locale], entries);
}