
window.addEventListener('scroll', function() {
    var backIcon = document.getElementById('back');
    var scrollPosition = window.pageYOffset || document.documentElement.scrollTop;

    if (scrollPosition > 1000) {
      backIcon.style.display = 'block';
    } else {
      backIcon.style.display = 'none';
    }
  });

  var backIcon = document.getElementById('back');
  backIcon.addEventListener('click', function(e) {
    e.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
    backIcon.style.display = 'none';
  });