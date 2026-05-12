// Scroll reveal
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      const siblings = e.target.parentElement.querySelectorAll('.reveal');
      siblings.forEach((el, i) => {
        setTimeout(() => el.classList.add('visible'), i * 100);
      });
      e.target.classList.add('visible');
    }
  });
}, { threshold: 0.08 });

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

// Mobile nav toggle
function toggleNav() {
  document.getElementById('nav-menu').classList.toggle('open');
}
