// swiper-init.js
// 질문 슬라이더 초기화 및 이벤트 처리

export function initSwiper(onQuestionClick) {
  const swiper = new Swiper(".swiper-container", {
    slidesPerView: "auto",
    spaceBetween: 8,
    freeMode: true,
  });

  const questionSlides = document.querySelectorAll(".swiper-slide");
  questionSlides.forEach(slide => {
    slide.addEventListener("click", () => {
      const question = slide.textContent.trim();
      if (question && typeof onQuestionClick === "function") {
        onQuestionClick(question);
      }
    });
  });
}