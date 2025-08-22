// api.js
// STT, TTS, 챗봇 답변 등 서버 API 통신 처리

import { getCookie } from "./utils.js";

const API_BASE = "/api/assistant";
const csrftoken = getCookie("csrftoken");

// 음성 인식(STT) 요청
export async function sendSttAudio(audioBlob) {
  const formData = new FormData();
  formData.append('audio', audioBlob);

  const res = await fetch(`${API_BASE}/stt/`, {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken },
    body: formData
  });
  return res.json();
}

// 챗봇 질문 전송
export async function sendQuestion({ text, assistantId, documentId, assistantDbId, fileSearch }) {
  const res = await fetch(`${API_BASE}/chatbot/${assistantDbId}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({
      assistant_id: assistantId,
      document_id: documentId,
      question: text,
      file_search: fileSearch,
    }),
  });
  return res.json();
}

// 음성 합성(TTS) 요청
export async function fetchTts({ text, assistantDbId }) {
  // text가 배열인 경우 문자열로 변환
  const plainText = Array.isArray(text) ? text.join("\n") : String(text);

  const res = await fetch(`${API_BASE}/tts/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ text: plainText, id: assistantDbId }),
  });

  return res.json();
}