(function () {
  const form = document.getElementById("langForm");
  const select = document.getElementById("langSelect");
  if (!form || !select) return;

  // URL 프리픽스 계산 (ko는 없음)
  function withLangPrefix(path, lang) {
    const supported = ["ko", "en", "ja", "fr", "de"];

    // 쿼리/해시 분리
    const url = new URL(window.location.origin + path);
    let pathname = url.pathname;

    // 기존 프리픽스 제거
    const parts = pathname.split("/");
    if (parts.length > 1 && supported.includes(parts[1])) {
      parts.splice(1, 1); // ex) /en/foo -> /foo
      pathname = parts.join("/") || "/";
    }

    // 새 프리픽스 적용
    if (lang !== "ko") {
      if (!pathname.startsWith("/")) pathname = "/" + pathname;
      pathname = `/${lang}${pathname}`;
    }
    url.pathname = pathname;
    return url.pathname + url.search + url.hash;
  }

  select.addEventListener("change", async function () {
    const lang = select.value;
    try {
      const formData = new FormData(form);
      formData.set("language", lang);

      // 세션/쿠키 갱신 위해 same-origin으로
      await fetch(form.action, {
        method: "POST",
        body: formData,
        credentials: "same-origin",
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });

      const target = withLangPrefix(
        window.location.pathname + window.location.search + window.location.hash,
        lang
      );
      window.location.assign(target);
    } catch (e) {
      console.error("Language switch failed:", e);
      form.submit(); // 폴백
    }
  });
})();