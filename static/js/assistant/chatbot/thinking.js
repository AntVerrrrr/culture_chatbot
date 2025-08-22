import { scrollToBottom } from "./utils.js";
import { _ } from "./i18n-helper.js";  // 다국어 대응 함수

const assistantProfileImgUrl = document.body.dataset.assistantImg || "/static/image/assistant/default-profile.png";
let thinkingMsgEl = null;
let thinkingInterval = null;

export function showThinking() {
  thinkingMsgEl = document.createElement("div");
  thinkingMsgEl.className = "message-container ai-message thinking";
  thinkingMsgEl.innerHTML = `
    <img src="${assistantProfileImgUrl}" alt="AI" class="profile-image">
    <div class="message-body">
      <div class="message-content">
        <p class="thinking-text">${_("생각 중")}</p>
      </div>
    </div>
  `;
  document.getElementById("messageList").appendChild(thinkingMsgEl);
  scrollToBottom();

  animateDots();
}

function animateDots() {
  const textEl = thinkingMsgEl.querySelector(".thinking-text");
  const baseText = _("생각 중");
  let dots = 0;

  thinkingInterval = setInterval(() => {
    if (!thinkingMsgEl || !textEl) {
      clearInterval(thinkingInterval);
      return;
    }
    textEl.textContent = baseText + '.'.repeat(dots);
    dots = (dots + 1) % 4;  // 0~3까지 반복
  }, 500);
}

export function removeThinking() {
  if (thinkingMsgEl) {
    thinkingMsgEl.remove();
    thinkingMsgEl = null;
  }
  clearInterval(thinkingInterval);
}