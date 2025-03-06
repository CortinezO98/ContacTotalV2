// Variables globales
const fullscreenHeader = document.getElementById('fullscreen-header');
const compactHeader = document.getElementById('compact-header');
const threshold = 100;
let isScrolling = false;

// Función para controlar el scroll con throttling
window.addEventListener('scroll', function() {
  if (!isScrolling) {
    window.requestAnimationFrame(function() {
      handleHeaderTransition();
      isScrolling = false;
    });
    isScrolling = true;
  }
});

// Función para manejar la transición de los headers
function handleHeaderTransition() {
  if (window.scrollY > threshold) {
    // Usuario ha scrolleado más allá del umbral
    if (!fullscreenHeader.classList.contains('hide')) {
      fullscreenHeader.classList.add('hide');
      compactHeader.classList.add('show');
    }
  } else {
    // Usuario ha regresado arriba del umbral
    if (fullscreenHeader.classList.contains('hide')) {
      fullscreenHeader.classList.remove('hide');
      compactHeader.classList.remove('show');
    }
  }
}