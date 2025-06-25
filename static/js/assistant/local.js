// find local

const cityData = {
  '서울': ['강남구', '종로구', '마포구', '서초구', '송파구', '영등포구'],
  '경기도': ['수원시', '성남시', '용인시', '고양시', '부천시', '남양주시'],
  '인천': ['미추홀구', '부평구', '연수구', '계양구', '남동구'],
  '강원도': ['춘천시', '원주시', '강릉시', '속초시', '동해시'],
  '충청북도': ['청주시', '충주시', '제천시', '옥천군', '음성군'],
  '충청남도': ['천안시', '아산시', '공주시', '논산시', '서산시'],
  '대전': ['서구', '유성구', '중구', '동구'],
  '세종': ['세종시'],
  '전라북도': ['전주시', '군산시', '익산시', '남원시', '김제시'],
  '전라남도': ['여수시', '순천시', '목포시', '광양시', '나주시'],
  '광주': ['서구', '북구', '남구', '동구', '광산구'],
  '경상북도': ['안동시', '경주시', '포항시', '구미시', '울진군', '영덕군'],
  '경상남도': ['창원시', '진주시', '김해시', '양산시', '거제시'],
  '대구': ['중구', '수성구', '달서구', '동구'],
  '울산': ['남구', '중구', '동구', '북구'],
  '부산': ['해운대구', '수영구', '동래구', '부산진구'],
  '제주도': ['제주시', '서귀포시']
};

$('.tag-scroll-wrapper .tag-button').on('click', function () {
  $('.tag-scroll-wrapper .tag-button').removeClass('selected');
  $(this).addClass('selected');

  const selectedProvince = $(this).data('province');
  $('#cityList').empty();
  $('#assistantList').empty();

  if (cityData[selectedProvince]) {
    cityData[selectedProvince].forEach(city => {
      $('#cityList').append(`<button class="tag-button" data-city="${city}">${city}</button>`);
    });
    $('.city-container').show();
  } else {
    $('.city-container').hide();
  }
});

$('#cityList').on('click', '.tag-button', function () {
  $('#cityList .tag-button').removeClass('selected');
  $(this).addClass('selected');

  const selectedCity = $(this).data('city');
  const selectedProvince = $('.tag-scroll-wrapper .tag-button.selected').data('province');

  $('#assistantList').empty();

  $.ajax({
    url: '/api/assistants/',
    method: 'GET',
    data: {
      province: selectedProvince,
      city_county_town: selectedCity
    },
    success: function (response) {
      if (response.length === 0) {
        $('#assistantList').append('<p>해당 지역에 어시스턴트가 없습니다.</p>');
      } else {
        response.forEach(assistant => {
          const tags = (assistant.tags || [])
            .sort((a, b) => a.priority - b.priority)
            .map(tag => `#${tag.name}`)
            .join(' ');

          $('#assistantList').append(`
            <div class="assistant-item">
              <a href="/chatbot/${assistant.id}/" onclick="setArrayIndex(1)">
                <div class="img-box">
                  <img src="${assistant.photo}" alt="${assistant.name}">
                </div>
                <p class="assistant-title">${assistant.name}</p>
                <p class="assistant-address">${tags}</p>
              </a>
            </div>
          `);
        });
      }
    },
    error: () => console.error('어시스턴트를 불러오는 데 실패했습니다.')
  });
});

function setArrayIndex(index) {
  sessionStorage.setItem('arrayIndex', index);
}

function enableHorizontalDragScroll(containerSelector) {
  const container = document.querySelector(containerSelector);
  let isDown = false;
  let startX, scrollLeft;

  container.addEventListener('mousedown', (e) => {
    isDown = true;
    container.classList.add('dragging');
    startX = e.pageX - container.offsetLeft;
    scrollLeft = container.scrollLeft;
  });

  container.addEventListener('mouseleave', () => {
    isDown = false;
    container.classList.remove('dragging');
  });

  container.addEventListener('mouseup', () => {
    isDown = false;
    container.classList.remove('dragging');
  });

  container.addEventListener('mousemove', (e) => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - container.offsetLeft;
    const walk = (x - startX) * 1.5; // 스크롤 속도 조절
    container.scrollLeft = scrollLeft - walk;
  });
}

// 실행 (시/도, 시군구)
enableHorizontalDragScroll('.tag-scroll-container');        // 첫 번째 슬라이더
enableHorizontalDragScroll('.city-container');              // 두 번째 슬라이더