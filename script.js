(function () {
  'use strict';

  var links = Array.prototype.slice.call(document.querySelectorAll('.nav-link'));
  var pages = Array.prototype.slice.call(document.querySelectorAll('.page-section'));
  var sidebar = document.getElementById('sidebar');
  var menuToggle = document.getElementById('menuToggle');

  function showPage() {
    var id = (window.location.hash || '#home').substring(1);
    var target = document.getElementById(id);
    var home = document.getElementById('home');
    var page = target && target.classList.contains('page-section') ? target : home;

    pages.forEach(function (item) {
      item.classList.toggle('active', item === page);
    });

    links.forEach(function (link) {
      link.classList.toggle('active', link.getAttribute('href') === '#' + page.id);
    });

    if (sidebar) sidebar.classList.remove('open');
    if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');

    // Contact/footer are anchors inside the home page, not separate pages.
    if (target && target !== page) {
      window.setTimeout(function () {
        if (target.scrollIntoView) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 0);
    } else {
      window.scrollTo(0, 0);
    }
  }

  window.addEventListener('hashchange', showPage);

  if (menuToggle && sidebar) {
    menuToggle.addEventListener('click', function () {
      var isOpen = sidebar.classList.toggle('open');
      menuToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
  }

  document.addEventListener('click', function (event) {
    if (window.innerWidth <= 720 && sidebar && sidebar.classList.contains('open')) {
      if (!sidebar.contains(event.target) && event.target !== menuToggle) {
        sidebar.classList.remove('open');
        if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
      }
    }
  });

  showPage();
}());
