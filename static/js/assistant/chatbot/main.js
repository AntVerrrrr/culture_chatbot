// main.js
// 모든 기능 초기화 진입점

import { initMicButton } from "./mic.js";
import { initSwiper } from "./swiper-init.js";
import { appendMessage } from "./message.js";
import { sendQuestion } from "./api.js";
import { showThinking, removeThinking } from "./thinking.js";

// DOM 로딩 완료 후 초기화
document.addEventListener("DOMContentLoaded", () => {
  const inputField = document.getElementById("messageInput");
  const sendButton = document.getElementById("sendButton");
  const assistantId = document.getElementById("assistant_id").value;
  const documentId = document.getElementById("document_id")?.value || null;
  const assistantDbId = parseInt(document.getElementById("assistant_db_id")?.value, 10);
  const profileImgUrl = document.getElementById("assistant_img_url")?.value;
  let fileSearchEnabled = false;

  // 질문 전송 핸들러
  async function submitQuestion(text) {
    if (!text || !assistantDbId || !assistantId) return;

    appendMessage(text, "user", assistantDbId);
    inputField.value = "";
    showThinking();

    try {
      const data = await sendQuestion({
        text,
        assistantId,
        assistantDbId,
        documentId,
        fileSearch: fileSearchEnabled,
      });

      removeThinking();
      appendMessage(data.response, "ai", assistantDbId, profileImgUrl);
    } catch (e) {
      removeThinking();
      alert("error: " + e.message);
    }
  }

  // 전송 버튼
  if (sendButton) {
    sendButton.addEventListener("click", () => {
      const text = inputField.value.trim();
      if (text) submitQuestion(text);
    });
  }

//  // 엔터 키 입력 처리
//  inputField?.addEventListener("keydown", (e) => {
//    if (e.key === "Enter" && !e.shiftKey) {
//      e.preventDefault();
//      const text = inputField.value.trim();
//      if (text) submitQuestion(text);
//    }
//  });

  // 교체본 (IME 대응)
  let composing = false;
  inputField?.addEventListener("compositionstart", () => { composing = true; });
  inputField?.addEventListener("compositionend",   () => { composing = false; });

  inputField?.addEventListener("keydown", (e) => {
    if (e.isComposing || composing || e.keyCode === 229) return; // ✅ 한글 조합 중이면 무시
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      const text = inputField.value.trim();
      if (text) submitQuestion(text);
    }
  });

  // 마이크 버튼 초기화
  initMicButton({
    onResult: (text) => {
      inputField.value = text;
      submitQuestion(text);
    },
  });

  // 질문 버블 초기화
  initSwiper((question) => {
    inputField.value = question;
    submitQuestion(question);
  });

  // 파일서치 버튼
  const fileSearchBtn = document.getElementById("fileSearchButton");
  fileSearchBtn?.addEventListener("click", () => {
    fileSearchEnabled = !fileSearchEnabled;
    fileSearchBtn.classList.toggle("active", fileSearchEnabled);
  });
});