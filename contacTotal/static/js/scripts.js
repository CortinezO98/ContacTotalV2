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

//Script de reproducción de radio
document.addEventListener('DOMContentLoaded', function() {
  const playButton = document.getElementById('play-button');
  const playIcon = document.getElementById('play-icon');
  const volumeSlider = document.getElementById('volume-slider');
  const volumeIcon = document.getElementById('volume-icon');

  if (!playButton || !playIcon || !volumeSlider || !volumeIcon) {
    console.error('One or more required DOM elements are missing.');
    return;
  }
  
  const audioElement = new Audio();
  audioElement.src = 'https://eu2.fastcast4u.com/proxy/julpar00?mp=/;';
  audioElement.preload = 'none';
  let isPlaying = false;
  
  // Función para actualizar el icono de volumen según el nivel
  function updateVolumeIcon(volume) {
    volumeIcon.className = '';
    if (volume === 0) {
      volumeIcon.className = 'fas fa-volume-mute';
    } else if (volume < 0.5) {
      volumeIcon.className = 'fas fa-volume-down';
    } else {
      volumeIcon.className = 'fas fa-volume-up';
    }
  }
  
  // Controlar la reproducción al hacer clic en el botón
  playButton.addEventListener('click', function() {
    if (!isPlaying) {
      playButton.classList.add('loading');
      
      audioElement.play()
        .then(() => {
          isPlaying = true;
          playIcon.className = 'fas fa-pause';
          playButton.classList.remove('loading');
        })
        .catch(error => {
          console.error('Error al reproducir el stream:', error);
          playButton.classList.remove('loading');
        });
    } else {
      audioElement.pause();
      isPlaying = false;
      playIcon.className = 'fas fa-play';
    }
  });
  
  // Controlar el volumen
  volumeSlider.addEventListener('input', function() {
    const volumeValue = parseFloat(this.value);
    audioElement.volume = volumeValue;
    updateVolumeIcon(volumeValue);
  });
  
  // Inicializar el volumen
  audioElement.volume = volumeSlider.value;
  updateVolumeIcon(audioElement.volume);
  
  // Manejar clics en el icono de volumen (silenciar/activar sonido)
  volumeIcon.addEventListener('click', function() {
    if (audioElement.volume > 0) {
      // Guardar el volumen actual antes de silenciar
      volumeIcon.dataset.previousVolume = audioElement.volume;
      audioElement.volume = 0;
      volumeSlider.value = 0;
      updateVolumeIcon(0);
    } else {
      // Restaurar el volumen anterior
      const previousVolume = parseFloat(volumeIcon.dataset.previousVolume || 0.8);
      audioElement.volume = previousVolume;
      volumeSlider.value = previousVolume;
      updateVolumeIcon(previousVolume);
    }
  });
});


