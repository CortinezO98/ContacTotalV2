window.onscroll = function() {
    handleScroll();
  };
  
  function handleScroll() {
    const header = document.getElementById('fullscreen-header');
    const compactHeader = document.getElementById('compact-header');
    
    if (window.scrollY > 100) { 
        header.classList.add('hide');
        compactHeader.classList.add('show');
    } else {
        header.classList.remove('hide');
        compactHeader.classList.remove('show');
    }
  }
  
  