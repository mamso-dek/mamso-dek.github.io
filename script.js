const yearSlot = document.querySelector("#year");
if (yearSlot) {
  yearSlot.textContent = new Date().getFullYear();
}

const revealItems = document.querySelectorAll(".reveal");

const observer = new IntersectionObserver(
  (entries, obs) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        obs.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.18 }
);

revealItems.forEach((item) => observer.observe(item));
