document.addEventListener("DOMContentLoaded", () => {
  const micButton = document.getElementById("sendTts");
  const inputField = document.getElementById("messageInput");
  const sendButton = document.getElementById("sendButton");
  const cancelMicBtn = document.getElementById("cancelMic");
  const fastResponseButton = document.getElementById("fastResponseButton");
  const messageList = document.getElementById("messageList");
  const assistantId = document.getElementById("assistant_id").value;
  const documentId = document.getElementById("document_id").value;
  const assistantDbId = document.getElementById("assistant_db_id").value;
  const csrftoken = getCookie("csrftoken");
  const assistantProfileImgUrl = document.body.dataset.assistantImg;

//  console.log("🟢 assistantDbId:", assistantDbId);

  let fastMode = false;
  let currentAudio = null;
  let mediaRecorder = null;
  let micStream = null;

  fastResponseButton?.addEventListener("click", () => {
    fastMode = !fastMode;
    console.log("⚡ fastMode 상태:", fastMode);
    fastResponseButton.classList.toggle("active", fastMode);
  });

  micButton?.addEventListener("click", async () => {
    micButton.disabled = true;
    inputField.placeholder = "듣는 중...";

    // 👇 입력창 숨기고 마이크 UI 표시
    document.getElementById("inputWrapper")?.classList.add("hidden");
    document.getElementById("voiceUi")?.classList.remove("hidden");

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
    const audioChunks = [];

    mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      const formData = new FormData();
      formData.append('audio', audioBlob);

      const sttRes = await fetch("/stt/", { method: "POST", body: formData }).then(res => res.json());
      const userText = sttRes.text;
      if (!userText) {
        appendMessage("(음성 인식 실패)", "ai");
        return;
      }
      appendMessage(userText, "user");

      const aiRes = await fetch(`/api/chatbot/${assistantDbId}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
        body: JSON.stringify({
          assistant_id: assistantId,
          document_id: documentId,
          question: userText,
          fast_response: fastMode,
        })
      }).then(res => res.json());

      const aiText = Array.isArray(aiRes.response) ? aiRes.response.join("\n") : aiRes.response;
      appendMessage(aiText, "ai");

      // 👇 마이크 UI 숨기고 입력창 다시 표시
      document.getElementById("inputWrapper")?.classList.remove("hidden");
      document.getElementById("voiceUi")?.classList.add("hidden");

      micButton.disabled = false;
      inputField.placeholder = "무엇이든 물어보세요...";
    };

    mediaRecorder.start();

    setTimeout(() => {
      mediaRecorder.stop();
      stream.getTracks().forEach((track) => track.stop());
    }, 3000);
  });

  cancelMicBtn?.addEventListener("click", () => {
    if (mediaRecorder && mediaRecorder.state !== "inactive") mediaRecorder.stop();
    if (micStream) micStream.getTracks().forEach(track => track.stop());

    document.getElementById("voiceUi")?.classList.add("hidden");
    document.getElementById("inputWrapper")?.classList.remove("hidden");
    micButton.disabled = false;
    inputField.placeholder = "무엇이든 물어보세요...";
  });

  sendButton?.addEventListener("click", () => {
    const msg = inputField.value.trim();
    if (msg) {
      inputField.value = "";  // 💡 먼저 비우기
      appendMessage(msg, "user");
      sendMessageToBackend(msg);
    }
  });

  inputField.addEventListener("keyup", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      const msg = inputField.value.trim();
      if (msg) {
        inputField.value = "";
        appendMessage(msg, "user");
        sendMessageToBackend(msg);
      }
    }
  });

  function appendMessage(text, sender) {
    const msgContainer = document.createElement("div");
    msgContainer.className = `message-container ${sender === "user" ? "user-message" : "ai-message"}`;

    if (sender === "ai") {
      const img = document.createElement("img");
      img.src = document.body.dataset.assistantImg;  // <body data-assistant-img="...">에서 가져옴
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

    // 🎯 마이크 UI 숨기고 입력창 다시 보이기
    document.getElementById("voiceUi")?.classList.add("hidden");
    document.getElementById("inputWrapper")?.classList.remove("hidden");

    if (sender === "ai") {
      let i = 0;
      let startedTTS = false;
      const chars = text.split("");
      const typingSpeed = 50;

      const typingInterval = setInterval(() => {
        if (i >= chars.length) {
          clearInterval(typingInterval);

          // 타이핑이 끝난 후에 버튼 추가
          const actions = createActionButtons();
          msgContent.appendChild(actions);

          scrollToBottom();
          return;
        }

        const char = chars[i];

        // 첫 글자 출력과 동시에 TTS 실행
        if (!startedTTS && i === 0) {
          playTTS(text);
          startedTTS = true;
        }

        if (char === "\n") {
          p.innerHTML += "<br>";
        } else {
          p.innerHTML += char;
        }

        scrollToBottom();
        i++;
      }, typingSpeed);
    } else {
      // 사용자 메시지는 즉시 출력
      const htmlText = text.replace(/\n/g, "<br>");
      p.innerHTML = htmlText;
    }
  }

  function sendMessageToBackend(text) {
    const stopThinking = showThinkingBubble();

    fetch(`/api/chatbot/${assistantDbId}/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
      body: JSON.stringify({
        assistant_id: assistantId,
        document_id: documentId,
        question: text,
        fast_response: fastMode,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        stopThinking();
        const response = Array.isArray(data.response) ? data.response.join("\n") : data.response;
        appendMessage(response, "ai");
      })
      .catch((err) => {
        console.error("❌ POST 전송 에러", err);
        appendMessage("⚠️ 답변을 불러오는 데 실패했어요.", "ai");
      });
  }

  // ✅ tts 재생 ------------------------------------------------------------------------------------------
  function playTTS(text) {
    console.log("📢 TTS 재생 요청:", text);
    console.log("🎯 assistantDbId:", assistantDbId);

    if (currentAudio) currentAudio.pause();

    fetch("/tts/", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
      body: JSON.stringify({
        text: text,
        id: assistantDbId
      })
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.audio_data) {
          currentAudio = new Audio(`data:audio/mpeg;base64,${data.audio_data}`);
          currentAudio.play();
        }
      });
  }

  // ✅ 화면 스크롤 ------------------------------------------------------------------------------------------
  function scrollToBottom() {
    const container = document.getElementById("chatContainer");
    container.scrollTop = container.scrollHeight;
  }

  // ✅ 쿠키 얻기 ------------------------------------------------------------------------------------------
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // ✅ 질문 버블 연결 ------------------------------------------------------------------------------------------
  document.querySelectorAll(".swiper-slide").forEach((slide) => {
    slide.addEventListener("click", () => {
      const text = slide.textContent.trim();
      if (text) {
        appendMessage(text, "user");
        sendMessageToBackend(text);
      }
    });
  });

  new Swiper(".swiper-container", {
    slidesPerView: "auto",
    spaceBetween: 10,
  });

  // ✅ 생각중 애니메이션 --------------------------------------------------------------------------------------------
  function showThinkingBubble() {
    const msgContainer = document.createElement("div");
    msgContainer.className = "message-container ai-message";
    msgContainer.id = "thinking-bubble";

    const profileImg = document.createElement("img");
    profileImg.className = "profile-image";
    profileImg.src = assistantProfileImgUrl;  // 아래에 선언한 전역 변수 사용
    profileImg.alt = "AI";

    msgContainer.appendChild(profileImg);

    const msgBody = document.createElement("div");
    msgBody.className = "message-body";

    const msgContent = document.createElement("div");
    msgContent.className = "message-content";

    const p = document.createElement("p");
    p.className = "thinking-dots";
    p.textContent = "고민 중.";

    msgContent.appendChild(p);
    msgBody.appendChild(msgContent);
    msgContainer.appendChild(msgBody);
    messageList.appendChild(msgContainer);

    scrollToBottom();

    // 🔁 점 애니메이션: . → .. → ... → .
    let dotCount = 1;
    const interval = setInterval(() => {
      dotCount = dotCount % 3 + 1;
      p.textContent = "고민 중" + ".".repeat(dotCount);
    }, 500);

    return () => {
      clearInterval(interval);
      msgContainer.remove();
    };
  }

  // ✅ 생각중 애니메이션 --------------------------------------------------------------------------------------------
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
    copyBtn.className = "action-button action-button-cp copy-btn";
    copyBtn.innerHTML = `<img src="${copyImgUrl}" alt="복사">`;
    copyBtn.addEventListener("click", () => {
      const content = wrapper.closest(".message-content").querySelector("p").innerText;
      navigator.clipboard.writeText(content);
      alert("복사되었습니다.");
    });

    actionBox.appendChild(likeBtn);
    actionBox.appendChild(unlikeBtn);
    actionBox.appendChild(copyBtn);

    wrapper.appendChild(hr);
    wrapper.appendChild(actionBox);

    return wrapper;
  }





});