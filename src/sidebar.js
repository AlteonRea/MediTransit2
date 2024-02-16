const navLinks = document.querySelectorAll(".nav-link");

var active = document.querySelector(".nav-link.active");

navLinks.forEach((navLink) => {
  navLink.addEventListener("mouseenter", () => {
    navLinks.forEach((link) => link.classList.remove("active"));
    navLink.classList.add("active");
  });

  navLink.addEventListener("mouseleave", () => {
    navLink.classList.remove("active");
    if (active) {
      active.classList.add("active");
    }
  });
});
