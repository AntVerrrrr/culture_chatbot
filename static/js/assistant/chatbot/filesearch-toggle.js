// filesearch-toggle.js
export function initFileSearchToggle({
  buttonId = "fileSearchButton",
  paramKey = "filesearch",
  onChange,
} = {}) {
  const btn = document.getElementById(buttonId);
  if (!btn) return null;

  const params = new URLSearchParams(location.search);
  let enabled = params.get(paramKey) === "1";

  // 초기 UI 반영
  sync();

  btn.addEventListener("click", () => {
    enabled = !enabled;
    sync();

    // URL 파라미터 갱신
    params.set(paramKey, enabled ? "1" : "0");
    history.replaceState(null, "", "?" + params.toString());

    if (typeof onChange === "function") onChange(enabled);
  });

  function sync() {
    btn.classList.toggle("active", enabled);
  }

  return {
    get enabled() { return enabled; },
    set(value) { enabled = !!value; sync(); },
  };
}