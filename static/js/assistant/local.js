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

  document.addEventListener('DOMContentLoaded', () => {
      const $assistantList = $('#assistantList');
      let inflight = 0;

      // province 클릭
      document.getElementById('provinceList')?.addEventListener('click', (e) => {
        const btn = e.target.closest('.tag-button');
        if (!btn) return;

        const pid = btn.dataset.provinceId;

        // 상위 선택 표시
        document.querySelectorAll('#provinceList .tag-button')
          .forEach(b => b.classList.toggle('selected', b === btn));

        // 모든 하위 그룹 숨김 + 해당 그룹만 show
        document.querySelectorAll('.city-group').forEach(g => {
          g.classList.toggle('show', g.dataset.provinceId === pid);
        });

        // 첫 도시 자동 선택
        const firstCityBtn = document.querySelector(`.city-group[data-province-id="${pid}"] .tag-button`);
        if (firstCityBtn) {
          firstCityBtn.click();
        } else {
          $assistantList.empty().html(`<p>해당 지역에 어시스턴트가 없습니다.</p>`);
        }
      });

      // city 클릭 시 Ajax 호출
      document.getElementById('cityList')?.addEventListener('click', (e) => {
        const btn = e.target.closest('.tag-button');
        if (!btn) return;

        const group = btn.closest('.city-group');
        const provinceId = group?.dataset.provinceId;
        const cityId = btn.dataset.cityId;

        group?.querySelectorAll('.tag-button').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');

        // 어시스턴트 로딩
        $assistantList.empty();
        const token = ++inflight;

        $.ajax({
          url: '/api/assistant/list/',
          method: 'GET',
          data: {
            province_id: provinceId,
            city_id: cityId,
            lang: (function () {
              const m = location.pathname.match(/^\/([a-z]{2})(\/|$)/i);
              return (m && m[1]) ? m[1].toLowerCase() : 'ko';
            })()
          },
          success: function (response) {
            if (token !== inflight) return;
            if (!Array.isArray(response) || response.length === 0) {
              $assistantList.html(`<p>해당 지역에 어시스턴트가 없습니다.</p>`);
              return;
            }
            renderAssistantCards($assistantList, response);
          },
          error: function () {
            if (token !== inflight) return;
            $assistantList.html(`<p>어시스턴트를 불러오는 데 실패했습니다.</p>`);
          }
        });
      });

      // 드래그 스크롤 적용
      enableHorizontalDragScroll('.tag-scroll-container');

      // 첫 province 자동 클릭
      document.querySelector('#provinceList .tag-button')?.click();
    });
})();