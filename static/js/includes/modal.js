document.addEventListener("DOMContentLoaded", function () {
  let lastFocused = null;

  // 열기: data-modal-target 사용
  document.body.addEventListener("click", function (e) {
    const opener = e.target.closest('[data-modal-target]');
    if (!opener) return;
    e.preventDefault();

    const id = opener.getAttribute('data-modal-target');
    const modal = document.getElementById(id);
    if (!modal) return;

    lastFocused = document.activeElement;
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('body-no-scroll');

    const focusTarget = modal.querySelector('.modal-close') || modal;
    focusTarget.focus();

    // ESC 닫기
    const onKeydown = (ev) => {
      if (ev.key === 'Escape') closeModal(modal, onKeydown);
    };
    document.addEventListener('keydown', onKeydown);

    // 닫기 핸들러 저장
    modal._escHandler = onKeydown;
  });

  // 닫기(닫기 버튼/백드롭)
  document.body.addEventListener("click", function (e) {
    const closer = e.target.closest('[data-modal-close]');
    if (!closer) return;

    const modal = closer.closest('.modal');
    if (!modal) return;

    closeModal(modal, modal._escHandler);
  });

  // 백드롭 직접 클릭도 닫기
  document.querySelectorAll('.modal .modal-backdrop').forEach(backdrop => {
    backdrop.addEventListener('click', function () {
      const modal = this.closest('.modal');
      closeModal(modal, modal._escHandler);
    });
  });

  function closeModal(modal, escHandler) {
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('body-no-scroll');
    if (escHandler) document.removeEventListener('keydown', escHandler);
    if (lastFocused) lastFocused.focus();
  }
});
