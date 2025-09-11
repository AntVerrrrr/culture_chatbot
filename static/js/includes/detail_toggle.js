
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".js-detail-toggle").forEach(trigger => {
    const targetSelector = trigger.dataset.target;
    const panel = document.querySelector(targetSelector);
    const chevron = trigger.querySelector(".chevron");

    trigger.addEventListener("click", (e) => {
      e.preventDefault();

      if (panel.hasAttribute("hidden")) {
        panel.removeAttribute("hidden");
        requestAnimationFrame(() => panel.classList.add("open"));
        chevron?.classList.add("rotate");
      } else {
        panel.classList.remove("open");
        chevron?.classList.remove("rotate");
        panel.addEventListener("transitionend", function onEnd(ev) {
          if (ev.propertyName === "max-height" && !panel.classList.contains("open")) {
            panel.setAttribute("hidden", "");
            panel.removeEventListener("transitionend", onEnd);
          }
        });
      }
    });
  });
});
