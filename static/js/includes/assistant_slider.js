// static/js/includes/assistant_slider.js
const swipers = [];
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.swiper-container').forEach((container) => {
        swipers.push(new Swiper(container, {
            loop: false,
            slidesPerView: 1.9,
            spaceBetween: 2,
            scrollbar: {
                el: container.querySelector('.swiper-scrollbar'),
                draggable: true,
            },
        }));
    });
});

function setArrayIndex(index) {
    sessionStorage.setItem('arrayIndex', index);
}