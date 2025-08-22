// mic.js
// 마이크 버튼 제어 및 STT 처리

import { sendSttAudio } from "./api.js";
import { _ } from "./i18n-helper.js";

let mediaRecorder;
let audioChunks = [];

export function initMicButton({
  micButtonId = "sendTts",
  cancelButtonId = "cancelMic",
  onResult,
}) {
  const micButton = document.getElementById(micButtonId);
  const cancelBtn = document.getElementById(cancelButtonId);
  const inputWrapper = document.getElementById("inputWrapper");
  const voiceUi = document.getElementById("voiceUi");
  const inputField = document.getElementById("messageInput");

  if (!micButton || !cancelBtn || !inputWrapper || !voiceUi) return;

  const originalPlaceholder = inputField.placeholder;

  micButton.addEventListener("click", async () => {
    inputWrapper.classList.add("hidden");
    voiceUi.classList.remove("hidden");
    micButton.disabled = true;
    inputField.placeholder = _("듣는 중...");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunks = [];
      mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.ondataavailable = (e) => {
        audioChunks.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const data = await sendSttAudio(audioBlob);
        if (data.text && typeof onResult === "function") {
          onResult(data.text);
        }
        stopMic();
      };

      mediaRecorder.start();
    } catch (err) {
      alert(_("마이크 접근에 실패했습니다."));
      stopMic();
    }
  });

  cancelBtn.addEventListener("click", stopMic);

  function stopMic() {
    inputWrapper.classList.remove("hidden");
    voiceUi.classList.add("hidden");
    micButton.disabled = false;
    inputField.placeholder = originalPlaceholder;

    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }
  }
}