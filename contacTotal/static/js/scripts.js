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
