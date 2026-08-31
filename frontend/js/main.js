/* ===================================================
   MAHI SOLAR – Main JavaScript
   =================================================== */

document.addEventListener('DOMContentLoaded', function () {

  /* ---- NAVBAR SCROLL EFFECT ---- */
  const navbar = document.getElementById('navbar') || document.querySelector('header');
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 20) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    });
  }

  /* ---- HAMBURGER MENU ---- */
  const hamburger = document.getElementById('hamburger');
  const navMenu = document.getElementById('navMenu');
  if (hamburger && navMenu) {
    hamburger.addEventListener('click', (e) => {
      e.stopPropagation();
      const isActive = navMenu.classList.toggle('active');
      hamburger.classList.toggle('open', isActive);
      hamburger.classList.toggle('active', isActive);
    });
    // Close menu when link is clicked
    navMenu.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        hamburger.classList.remove('open');
        hamburger.classList.remove('active');
      });
    });
    // Close on outside click
    document.addEventListener('click', (e) => {
      const header = document.getElementById('navbar') || document.querySelector('header');
      if (header && !header.contains(e.target) && !navMenu.contains(e.target)) {
        navMenu.classList.remove('active');
        hamburger.classList.remove('open');
        hamburger.classList.remove('active');
      }
    });
  }


  /* ---- THEME TOGGLE ---- */
  const themeToggle = document.getElementById('themeToggle');
  const html = document.documentElement;
  const savedTheme = localStorage.getItem('mahi_theme') || 'dark';
  html.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  if (themeToggle) {
    themeToggle.addEventListener('click', (e) => {
      e.preventDefault();
      const current = html.getAttribute('data-theme') || 'dark';
      const next = current === 'light' ? 'dark' : 'light';
      html.setAttribute('data-theme', next);
      localStorage.setItem('mahi_theme', next);
      updateThemeIcon(next);
    });
  }

  function updateThemeIcon(theme) {
    if (!themeToggle) return;
    const icon = themeToggle.querySelector('i');
    if (icon) {
      icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
  }

  /* ---- AUTO DISMISS MESSAGES ---- */
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.animation = 'fadeOut 0.4s ease forwards';
      setTimeout(() => alert.remove(), 400);
    }, 5000);
  });

  /* ---- ACTIVE NAV LINK ---- */
  const currentPath = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath || (currentPath === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });

  /* ---- PAYMENT METHOD UI ---- */
  document.querySelectorAll('input[name="payment_method"]').forEach(radio => {
    radio.addEventListener('change', function () {
      document.querySelectorAll('.payment-card').forEach(card => {
        card.style.borderColor = '';
        card.style.background = '';
      });
    });
  });

  /* ---- CART QUANTITY BUTTONS ---- */
  document.querySelectorAll('.qty-form').forEach(form => {
    form.querySelectorAll('.qty-btn').forEach(btn => {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        const quantity = parseInt(this.value);
        if (quantity === 0) {
          if (confirm('Remove this item from cart?')) {
            this.form.querySelector('[name="quantity"]') || (this.type = 'submit');
            this.form.submit();
          }
        } else {
          const input = document.createElement('input');
          input.type = 'hidden';
          input.name = 'quantity';
          input.value = quantity;
          form.appendChild(input);
          form.submit();
        }
      });
    });
  });

  /* ---- SCROLL REVEAL ---- */
  const revealElements = document.querySelectorAll(
    '.product-card, .blog-card, .stat-card, .testimonial-card, .info-card, .result-card'
  );
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    revealElements.forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(16px)';
      el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      observer.observe(el);
    });
  }

  /* ---- SMOOTH COUNTER ANIMATION ---- */
  function animateCounter(el, target, duration = 1500) {
    let start = 0;
    const step = (timestamp) => {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      el.textContent = Math.floor(progress * target).toLocaleString('en-IN');
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  const counters = document.querySelectorAll('[data-count]');
  if ('IntersectionObserver' in window && counters.length > 0) {
    const counterObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target, parseInt(entry.target.dataset.count));
          counterObserver.unobserve(entry.target);
        }
      });
    });
    counters.forEach(c => counterObserver.observe(c));
  }

  /* ---- PRODUCT IMAGE LAZY LOAD ---- */
  if ('IntersectionObserver' in window) {
    const lazyImages = document.querySelectorAll('img[data-src]');
    const imgObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.src = entry.target.dataset.src;
          imgObserver.unobserve(entry.target);
        }
      });
    });
    lazyImages.forEach(img => imgObserver.observe(img));
  }

  /* ---- DATE MIN FOR SITE VISIT ---- */
  const dateInput = document.querySelector('input[name="preferred_date"]');
  if (dateInput) {
    const today = new Date();
    today.setDate(today.getDate() + 1); // Min next day
    dateInput.min = today.toISOString().split('T')[0];
  }

});

/* ---- GLOBAL: TOGGLE PASSWORD ---- */
function togglePassword(inputId, btn) {
  const input = document.getElementById(inputId);
  if (!input) return;
  const isHidden = input.type === 'password';
  input.type = isHidden ? 'text' : 'password';
  const icon = btn.querySelector('i');
  if (icon) {
    icon.className = isHidden ? 'fas fa-eye-slash' : 'fas fa-eye';
  }
}

/* ---- ADD TO CART AJAX ---- */
function addToCartAjax(productId, btn) {
  const apiBase = window.API_BASE_URL || 'http://127.0.0.1:8000';
  fetch(`${apiBase}/api/cart/add_item/`, {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    credentials: 'include',
    body: JSON.stringify({ product_id: parseInt(productId, 10) }),
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      const cartCount = data.cart?.item_count ?? data.cart_count;
      const badge = document.querySelector('.cart-badge');
      if (badge) {
        badge.textContent = cartCount;
      } else {
        const cartBtn = document.querySelector('.cart-btn');
        if (cartBtn) {
          const span = document.createElement('span');
          span.className = 'cart-badge';
          span.textContent = cartCount;
          cartBtn.appendChild(span);
        }
      }
      if (btn) {
        btn.textContent = '✓ Added!';
        btn.style.background = '#43a047';
        setTimeout(() => {
          btn.innerHTML = '<i class="fas fa-cart-plus"></i> Add to Cart';
          btn.style.background = '';
        }, 1500);
      }
    }
  })
  .catch(() => {});
}

function getCsrfToken() {
  const name = 'csrftoken';
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}

/* ---- ADD FADE-OUT ANIMATION ---- */
const style = document.createElement('style');
style.textContent = `
@keyframes fadeOut {
  from { opacity: 1; transform: translateX(0); }
  to { opacity: 0; transform: translateX(100%); }
}
.nav-link.active { color: var(--solar-gold) !important; }
`;
document.head.appendChild(style);
