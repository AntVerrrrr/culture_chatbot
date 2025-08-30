document.addEventListener("DOMContentLoaded", () => {
  const select  = document.getElementById("langSelect");
  const trigger = document.getElementById("langTrigger");
  const panel   = document.getElementById("langPanel");
  const flagImg = document.getElementById("langTriggerFlag");
  const labelEl = document.getElementById("langTriggerLabel");
  if (!select || !trigger || !panel) return;

  function updateTrigger(code, label) {
    flagImg.src = `/static/image/includes/language_dropdown/${code}.png`;
    labelEl.textContent = label || code.toUpperCase(); // 라벨 우선, 없으면 약어
  }

  // 초기 표시: select의 선택 옵션에서 라벨 읽기
  const selOpt = select.options[select.selectedIndex];
  updateTrigger(select.value, selOpt?.dataset.label || selOpt?.textContent || select.value.toUpperCase());

  // 열기/닫기
  function openPanel(){ panel.classList.add("open"); trigger.setAttribute("aria-expanded","true"); }
  function closePanel(){ panel.classList.remove("open"); trigger.setAttribute("aria-expanded","false"); }
  trigger.addEventListener("click", (e) => { e.stopPropagation(); panel.classList.contains("open") ? closePanel() : openPanel(); });
  document.addEventListener("click", (e) => { if (!panel.contains(e.target) && e.target !== trigger) closePanel(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closePanel(); });

  // 항목 클릭: 코드/라벨 함께 적용
  panel.querySelectorAll(".lang-item").forEach(btn => {
    btn.addEventListener("click", () => {
      const code  = btn.dataset.lang;
      const label = btn.dataset.label;
      // select 값 변경 → 기존 language_dropdown.js가 /i18n/setlang/ POST + 이동 처리
      select.value = code;
      updateTrigger(code, label);
      closePanel();
      select.dispatchEvent(new Event("change", { bubbles:true }));
    });
  });
});