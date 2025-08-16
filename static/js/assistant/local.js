// static/js/assistant/local.js
(function () {
  'use strict';

  // jsi18n 준비 전이면 원문 그대로
  const _ = (typeof gettext === 'function') ? gettext : (s) => s;

  function currentLang() {
    const m = location.pathname.match(/^\/([a-z]{2})(\/|$)/i);
    return (m && m[1]) ? m[1].toLowerCase() : 'ko';
  }
  function buildChatbotUrl(id) {
    const lang = currentLang();
    return (lang === 'ko') ? `/chatbot/${id}/` : `/${lang}/chatbot/${id}/`;
  }
  function toAbs(url) {
    if (!url) return '';
    try { return new URL(url, location.origin).href; } catch { return url; }
  }

  function renderAssistantCards($assistantList, items) {
    const frag = document.createDocumentFragment();

    for (let i = 0; i < items.length; i++) {
      const aData = items[i];

      const wrap = document.createElement('div');
      wrap.className = 'assistant-item';

      const a = document.createElement('a');
      a.href = buildChatbotUrl(aData.id);
      a.addEventListener('click', () => {
        try { sessionStorage.setItem('arrayIndex', 1); } catch (_) {}
      });

      const imgBox = document.createElement('div');
      imgBox.className = 'img-box';

      const img = document.createElement('img');
      img.src = toAbs(aData.photo);
      img.alt = aData.name || 'assistant';

      const title = document.createElement('p');
      title.className = 'assistant-title';
      title.textContent = aData.name || '';

      const addr = document.createElement('p');
      addr.className = 'assistant-address';
      const tags = (aData.tags || [])
        .slice()
        .sort((x, y) => (x.priority || 0) - (y.priority || 0))
        .map(t => `#${t.name}`)
        .join(' ');
      addr.textContent = tags;

      imgBox.appendChild(img);
      a.appendChild(imgBox);
      a.appendChild(title);
      a.appendChild(addr);
      wrap.appendChild(a);
      frag.appendChild(wrap);
    }
    $assistantList.empty()[0].appendChild(frag);
  }

  function enableHorizontalDragScroll(selector) {
    const el = document.querySelector(selector);
    if (!el) return;

    let isDown = false, startX = 0, scrollLeft = 0;
    const onDown = (pageX) => { isDown = true; el.classList.add('dragging'); startX = pageX - el.offsetLeft; scrollLeft = el.scrollLeft; };
    const onMove = (pageX, preventDefault) => {
      if (!isDown) return;
      if (preventDefault) preventDefault();
      const x = pageX - el.offsetLeft;
      el.scrollLeft = scrollLeft - (x - startX) * 1.5;
    };
    const onUp = () => { isDown = false; el.classList.remove('dragging'); };

    el.addEventListener('mousedown', (e) => onDown(e.pageX));
    el.addEventListener('mousemove', (e) => onMove(e.pageX, () => e.preventDefault()));
    el.addEventListener('mouseup', onUp);
    el.addEventListener('mouseleave', onUp);

    el.addEventListener('touchstart', (e) => onDown(e.touches[0].pageX), { passive: true });
    el.addEventListener('touchmove',  (e) => onMove(e.touches[0].pageX, null), { passive: true });
    el.addEventListener('touchend', onUp, { passive: true });
  }

  document.addEventListener('DOMContentLoaded', function () {
    const $provinceList  = $('#provinceList');
    const $assistantList = $('#assistantList');
    const cityContainer  = document.querySelector('.city-container'); // 그룹 전체 감싸는 컨테이너
    let inflight = 0; // 중복 요청 제어용 토큰

    // 상위 지역 클릭 → 해당 city-group만 표시 + 첫 도시 자동 선택
    document.getElementById('provinceList')?.addEventListener('click', (e) => {
      const btn = e.target.closest('.tag-button');
      if (!btn) return;

      const pid = btn.dataset.provinceId;  // 숫자 id (문자열 비교 OK)

      // 선택 표시
      document.querySelectorAll('#provinceList .tag-button')
        .forEach(b => b.classList.toggle('selected', b === btn));

      // 해당 시군구 그룹만 표시
      const groups = document.querySelectorAll('.city-group');
      let anyShown = false;
      groups.forEach(g => {
        const show = (g.dataset.provinceId === pid);
        g.hidden = !show;
        if (show) anyShown = true;
      });

      // 컨테이너 표시/숨김
      if (cityContainer) cityContainer.style.display = anyShown ? 'block' : 'none';

      // 첫 도시 자동 선택
      const firstCityBtn = document.querySelector(`.city-group[data-province-id="${pid}"] .tag-button`);
      if (firstCityBtn) {
        firstCityBtn.click();
      } else {
        $assistantList.empty().html(`<p>${_('해당 지역에 어시스턴트가 없습니다.')}</p>`);
      }
    });

    // 하위 지역 클릭 → 어시스턴트 목록 로드
    document.getElementById('cityList')?.addEventListener('click', (e) => {
      const btn = e.target.closest('.tag-button');
      if (!btn) return;

      const group = btn.closest('.city-group');
      const provinceId = group?.dataset.provinceId;
      const cityId = btn.dataset.cityId;

      // 선택 표시
      group?.querySelectorAll('.tag-button').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');

      // Ajax로 id 기반 조회
      $assistantList.empty();
      const token = ++inflight;

      $.ajax({
        url: '/api/assistant/list/',
        method: 'GET',
        data: {
            province_id: provinceId,
            city_id: cityId,
            lang: (function(){
              const m = location.pathname.match(/^\/([a-z]{2})(\/|$)/i);
              return (m && m[1]) ? m[1].toLowerCase() : 'ko';
            })()
          },
        success: function (response) {
          if (token !== inflight) return; // 최신 응답만 반영
          if (!Array.isArray(response) || response.length === 0) {
            $assistantList.html(`<p>${_('해당 지역에 어시스턴트가 없습니다.')}</p>`);
            return;
          }
          renderAssistantCards($assistantList, response);
        },
        error: function () {
          if (token !== inflight) return;
          console.error(_('어시스턴트를 불러오는 데 실패했습니다.'));
          $assistantList.html(`<p>${_('어시스턴트를 불러오는 데 실패했습니다.')}</p>`);
        }
      });
    });

    // 드래그 스크롤
    enableHorizontalDragScroll('.tag-scroll-container');
    enableHorizontalDragScroll('.city-container');

    // 첫 상위 지역 자동 선택
    document.querySelector('#provinceList .tag-button')?.click();
  });
})();