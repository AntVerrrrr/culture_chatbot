// message.js
// 메시지 출력, 타이핑 효과, 복사 버튼 등 UI 구성

import { scrollToBottom } from "./utils.js";
import { fetchTts } from "./api.js";
import { _ } from "./i18n-helper.js";

// 전역에서 설정되는 이미지 URL
const likeImgUrl = "/static/image/assistant/like.svg";
const unlikeImgUrl = "/static/image/assistant/unlike.svg";
const copyImgUrl = "/static/image/assistant/copy.svg";

// 현재 오디오 재생 인스턴스
let currentAudio = null;

// TTS 실행
function playTTS(text, assistantDbId) {
  if (currentAudio) currentAudio.pause();

  fetchTts({ text, assistantDbId }).then(data => {
    if (data.audio_data) {
      currentAudio = new Audio(`data:audio/mpeg;base64,${data.audio_data}`);
      currentAudio.play();
    }
  });
}

// 메시지 출력
export function appendMessage(text, sender, assistantDbId, profileImgUrl) {
  const messageList = document.getElementById("messageList");

  const msgContainer = document.createElement("div");
  msgContainer.className = `message-container ${sender === "user" ? "user-message" : "ai-message"}`;

  if (sender === "ai") {
    const img = document.createElement("img");

    const defaultProfileImg = document.body.dataset.assistantImg || "/static/image/assistant/default-profile.png";
    img.src = profileImgUrl || defaultProfileImg;

    img.alt = "assistant-profile";
    img.className = "profile-image";
    msgContainer.appendChild(img);
  }

  const msgBody = document.createElement("div");
  msgBody.className = "message-body";

  const msgContent = document.createElement("div");
  msgContent.className = "message-content";

  const p = document.createElement("p");
  msgContent.appendChild(p);
  msgBody.appendChild(msgContent);
  msgContainer.appendChild(msgBody);
  messageList.appendChild(msgContainer);

  scrollToBottom();

  if (sender === "ai") {
    let i = 0;
    let startedTTS = false;
//    console.log("text: ", text, typeof text);
    const textStr = Array.isArray(text) ? text[0] : String(text);
    const chars = textStr.split("");
    const typingSpeed = 50;

    const typingInterval = setInterval(() => {
      if (i >= chars.length) {
        clearInterval(typingInterval);
        const actions = createActionButtons();
        msgContent.appendChild(actions);
        scrollToBottom();
        return;
      }

      const char = chars[i];
      if (!startedTTS && i === 0) {
        playTTS(text, assistantDbId);
        startedTTS = true;
      }

      p.innerHTML += (char === "\n") ? "<br>" : char;
      scrollToBottom();
      i++;
    }, typingSpeed);
  } else {
    p.innerHTML = text.replace(/\n/g, "<br>");
  }
}

// AI 메시지 액션 버튼 (좋아요, 싫어요, 복사)
function createActionButtons() {
  const wrapper = document.createElement("div");
  wrapper.className = "actions-wrapper";

  const hr = document.createElement("hr");
  hr.className = "msg-hr";

  const actionBox = document.createElement("div");
  actionBox.className = "message-actions";

  const likeBtn = document.createElement("button");
  likeBtn.className = "action-button like-btn";
  likeBtn.innerHTML = `<img src="${likeImgUrl}" alt="좋아요">`;

  const unlikeBtn = document.createElement("button");
  unlikeBtn.className = "action-button unlike-btn";
  unlikeBtn.innerHTML = `<img src="${unlikeImgUrl}" alt="싫어요">`;

  const copyBtn = document.createElement("button");
  copyBtn.className = "action-button copy-btn";
  copyBtn.innerHTML = `<img src="${copyImgUrl}" alt="복사">`;
  copyBtn.addEventListener("click", () => {
    const content = wrapper.closest(".message-content").querySelector("p").innerText;
    navigator.clipboard.writeText(content);
    alert(_("copy."));
  });

  actionBox.appendChild(likeBtn);
  actionBox.appendChild(unlikeBtn);
  actionBox.appendChild(copyBtn);
  wrapper.appendChild(hr);
  wrapper.appendChild(actionBox);

  return wrapper;
}