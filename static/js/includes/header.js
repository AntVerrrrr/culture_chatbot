document.addEventListener("DOMContentLoaded", () => {
  const menuButton = document.getElementById("menuButton");
  const sideDrawer = document.getElementById("sideDrawer");
  const drawerOverlay = document.getElementById("drawerOverlay");

  function openDrawer() {
    sideDrawer.classList.add("open");
    drawerOverlay.classList.add("active");
  }

  function closeDrawer() {
    sideDrawer.classList.remove("open");
    drawerOverlay.classList.remove("active");
  }

  if (menuButton && sideDrawer && drawerOverlay) {
    menuButton.addEventListener("click", (e) => {
      e.stopPropagation();
      openDrawer();
    });

    drawerOverlay.addEventListener("click", (e) => {
      e.preventDefault();
      closeDrawer();
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        closeDrawer();
      }
    });
  }
});