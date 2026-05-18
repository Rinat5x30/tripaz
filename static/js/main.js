/* TripAZ — Premium UI Interactions */

document.addEventListener('DOMContentLoaded', () => {
  initPageLoader();
  initNavbar();
  initAlerts();
  initMobileMenu();
  initFavoriteButtons();
  initCardNumberFormat();
  initScrollReveal();
  initParallax();
});

/* Page loader */
function initPageLoader() {
  const loader = document.getElementById('page-loader');
  if (!loader) return;

  const hide = () => {
    loader.classList.add('hidden');
    setTimeout(() => loader.remove(), 500);
  };

  if (document.readyState === 'complete') {
    setTimeout(hide, 400);
  } else {
    window.addEventListener('load', () => setTimeout(hide, 300));
    setTimeout(hide, 2500); // fallback: hide if fonts/external resources are slow
  }
}

/* Navbar scroll behavior */
function initNavbar() {
  const navbar = document.getElementById('site-navbar');
  if (!navbar) return;

  const isHome = document.body.classList.contains('page-home');

  if (isHome) {
    navbar.classList.add('navbar--transparent', 'navbar--hero');
    navbar.classList.remove('navbar--solid');
  }

  const onScroll = () => {
    const scrolled = window.scrollY > 60;

    if (isHome) {
      navbar.classList.toggle('navbar--scrolled', scrolled);
      navbar.classList.toggle('navbar--transparent', !scrolled);
      navbar.classList.toggle('navbar--hero', !scrolled);
    } else {
      navbar.classList.toggle('navbar--scrolled', scrolled);
    }
  };

  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
}

/* Flash messages */
function initAlerts() {
  document.querySelectorAll('.alert').forEach(alert => {
    const close = alert.querySelector('.alert-close');
    if (close) close.addEventListener('click', () => dismissAlert(alert));
    setTimeout(() => dismissAlert(alert), 5500);
  });
}

function dismissAlert(alert) {
  alert.style.opacity = '0';
  alert.style.transform = 'translateX(20px)';
  alert.style.transition = '0.35s cubic-bezier(0.16, 1, 0.3, 1)';
  setTimeout(() => alert.remove(), 350);
}

/* Mobile menu */
function initMobileMenu() {
  const hamburger = document.querySelector('.hamburger');
  const mobileMenu = document.getElementById('mobile-menu');
  const mobileClose = document.querySelector('.mobile-close');

  if (!hamburger || !mobileMenu) return;

  const open = () => {
    mobileMenu.classList.add('open');
    mobileMenu.setAttribute('aria-hidden', 'false');
    document.body.classList.add('nav-open');
  };

  const close = () => {
    mobileMenu.classList.remove('open');
    mobileMenu.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('nav-open');
  };

  hamburger.addEventListener('click', open);
  mobileClose?.addEventListener('click', close);

  mobileMenu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', close);
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && mobileMenu.classList.contains('open')) close();
  });

  document.addEventListener('click', e => {
    if (mobileMenu.classList.contains('open') && !mobileMenu.contains(e.target) && e.target !== hamburger) close();
  });
}

/* Favorites */
function initFavoriteButtons() {
  document.querySelectorAll('.fav-btn').forEach(btn => {
    btn.addEventListener('click', async e => {
      e.preventDefault();
      e.stopPropagation();
      const guideId = btn.dataset.guideId;
      if (!guideId) return;

      btn.style.transform = 'scale(0.85)';
      setTimeout(() => { btn.style.transform = ''; }, 150);

      try {
        const res = await fetch(`/guides/${guideId}/favorite/`, {
          method: 'POST',
          headers: { 'X-CSRFToken': getCsrf() },
        });
        const data = await res.json();
        btn.classList.toggle('active', data.status === 'added');
        btn.textContent = data.status === 'added' ? '❤️' : '🤍';
      } catch (err) {
        console.error('Favorite toggle failed', err);
      }
    });
  });
}

/* Payment card formatting */
function initCardNumberFormat() {
  const cardInput = document.querySelector('input[name="card_number"]');
  if (!cardInput) return;

  cardInput.addEventListener('input', e => {
    let value = e.target.value.replace(/\D/g, '').slice(0, 16);
    e.target.value = value.replace(/(.{4})/g, '$1 ').trim();

    const preview = document.querySelector('.card-number');
    if (preview) {
      const padded = value.padEnd(16, '•');
      preview.textContent = padded.replace(/(.{4})/g, '$1 ').trim();
    }
  });

  const nameInput = document.querySelector('input[name="cardholder_name"]');
  nameInput?.addEventListener('input', e => {
    const el = document.querySelector('.card-holder-name');
    if (el) el.textContent = e.target.value.toUpperCase() || 'CARDHOLDER NAME';
  });
}

/* Scroll reveal */
function initScrollReveal() {
  const reveals = document.querySelectorAll('.reveal');
  if (!reveals.length) return;

  const observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
  );

  reveals.forEach(el => observer.observe(el));
}

/* Subtle parallax on hero */
function initParallax() {
  const parallaxEls = document.querySelectorAll('[data-parallax]');
  if (!parallaxEls.length) return;

  const onScroll = () => {
    const scrollY = window.scrollY;
    parallaxEls.forEach(el => {
      const speed = parseFloat(el.dataset.parallax) || 0.3;
      el.style.transform = `translate3d(0, ${scrollY * speed}px, 0)`;
    });
  };

  window.addEventListener('scroll', onScroll, { passive: true });
}

function getCsrf() {
  return document.cookie.split('; ')
    .find(c => c.startsWith('csrftoken='))
    ?.split('=')[1] || '';
}

/* Booking calendar */
function initBookingCalendar(availableDates) {
  const dateInput = document.querySelector('input[name="booking_date"]');
  if (!dateInput || !availableDates) return;

  dateInput.addEventListener('input', () => {
    const selected = dateInput.value;
    const msg = document.querySelector('.date-availability-msg');
    if (!msg) return;

    if (availableDates.includes(selected)) {
      msg.textContent = '✓ Guide is available on this date';
      msg.className = 'form-hint text-success';
    } else if (selected) {
      msg.textContent = '⚠ Guide may not be available — they will confirm your request';
      msg.className = 'form-hint text-warning';
    } else {
      msg.textContent = '';
    }
  });
}

/* Price calculator */
function initPriceCalculator(hourlyRate) {
  const peopleInput = document.querySelector('input[name="people_count"]');
  const tourSelect = document.querySelector('select[name="tour"]');
  const totalDisplay = document.querySelector('.total-price-display');

  function recalc() {
    const people = parseInt(peopleInput?.value) || 1;
    const price = hourlyRate * people;
    if (totalDisplay) totalDisplay.textContent = `~${price.toFixed(2)} AZN`;
  }

  peopleInput?.addEventListener('input', recalc);
  tourSelect?.addEventListener('change', recalc);
  recalc();
}
