// utils.js
// 공통 유틸 함수 모음

// 채팅창을 아래로 스크롤
export function scrollToBottom() {
  const container = document.getElementById("chatContainer");
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

// 쿠키에서 특정 이름의 값 얻기
export function getCookie(name) {
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