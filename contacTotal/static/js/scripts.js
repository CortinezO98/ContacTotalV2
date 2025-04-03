window.onscroll = function() {
  const fullscreenHeader = document.getElementById('fullscreen-header');
  const compactHeader = document.getElementById('compact-header');
  const threshold = 100;

  if (window.scrollY > threshold) {
    fullscreenHeader.classList.remove('fast');
    fullscreenHeader.classList.add('slow', 'hide');

    compactHeader.classList.remove('fast');
    compactHeader.classList.add('slow', 'show');
  } else {
    fullscreenHeader.classList.remove('slow', 'hide');
    fullscreenHeader.classList.add('fast');

    compactHeader.classList.remove('slow', 'show');
    compactHeader.classList.add('fast');
    
  }
};

document.addEventListener("DOMContentLoaded", function() {
  // Seleccionamos el carrusel
  const carousel = document.getElementById('noticiasCarousel');
  
  // Aseguramos que el intervalo sea más largo para dar tiempo a leer
  const bsCarousel = new bootstrap.Carousel(carousel, {
    interval: 5000,
    wrap: true
  });
  
  // Agregamos transiciones suaves a las tarjetas
  const addSmoothTransition = () => {
    const cards = document.querySelectorAll('#noticiasCarousel .card');
    cards.forEach(card => {
      if (!card.classList.contains('transition-added')) {
        card.style.transition = 'opacity 0.3s ease';
        card.classList.add('transition-added');
      }
    });
  };
  
  // Aplicamos la transición inicial
  addSmoothTransition();
  
  // Mejoramos la experiencia de transición
  carousel.addEventListener('slide.bs.carousel', function(event) {
    const activeSlide = carousel.querySelector('.carousel-item.active');
    const cards = activeSlide.querySelectorAll('.card');
    
    // Fade out
    cards.forEach(card => {
      card.style.opacity = '0.5';
    });
  });
  
  carousel.addEventListener('slid.bs.carousel', function(event) {
    const activeSlide = carousel.querySelector('.carousel-item.active');
    const cards = activeSlide.querySelectorAll('.card');
    
    // Fade in
    cards.forEach(card => {
      setTimeout(() => {
        card.style.opacity = '1';
      }, 50);
    });
    
    // Aseguramos que las transiciones estén aplicadas a todas las tarjetas
    addSmoothTransition();
  });
});