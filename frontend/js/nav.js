/**
 * Flock — Shared Navigation Logic
 * Handles: active sidebar state, mobile drawer toggle, page title in TopAppBar
 */

(function () {
  // ── Page map ─────────────────────────────────────────────────────────────
  const PAGE_MAP = {
    'index.html':     { label: 'Home',                icon: 'home' },
    'explorer.html':  { label: 'Stock Explorer',       icon: 'search' },
    'portfolio.html': { label: 'Portfolio Simulator',  icon: 'pie_chart' },
    'sip.html':       { label: 'SIP Calculator',       icon: 'trending_up' },
  };

  const current = location.pathname.split('/').pop() || 'index.html';
  const pageInfo = PAGE_MAP[current] || { label: 'Flock', icon: 'home' };

  // ── Update TopAppBar title ────────────────────────────────────────────────
  document.querySelectorAll('[data-page-title]').forEach(el => {
    el.textContent = pageInfo.label;
  });

  // Fallback: find the span inside header that says "Welcome to Flock"
  document.querySelectorAll('header .font-headline, header span.font-headline').forEach(el => {
    if (el.textContent.trim() === 'Welcome to Flock') {
      el.textContent = pageInfo.label;
    }
  });

  // ── Fix sidebar links & set active state ─────────────────────────────────
  const NAV_LINKS = {
    'index.html':     ['/index.html', 'Home', 'Dashboard'],
    'explorer.html':  ['/explorer.html', 'Explorer', 'Stock Explorer'],
    'portfolio.html': ['/portfolio.html', 'Portfolio', 'Simulator'],
    'sip.html':       ['/sip.html', 'SIP', 'Planner'],
  };

  document.querySelectorAll('aside a, aside nav a').forEach(link => {
    const text = link.textContent.trim().toLowerCase();
    let targetPage = null;

    if (text.includes('home') || text.includes('dashboard')) targetPage = '/index.html';
    else if (text.includes('explorer') || text.includes('stock')) targetPage = '/explorer.html';
    else if (text.includes('portfolio') || text.includes('simulator')) targetPage = '/portfolio.html';
    else if (text.includes('sip') || text.includes('planner')) targetPage = '/sip.html';

    if (targetPage) {
      link.href = targetPage;
      const isActive = targetPage === '/' + current || (current === '' && targetPage === '/index.html');
      if (isActive) {
        link.classList.add('text-primary', 'bg-surface-container-lowest', 'shadow-sm');
        link.classList.remove('text-on-surface-variant', 'text-[#404943]');
      }
    }
  });

  // ── Mobile hamburger drawer ───────────────────────────────────────────────
  const sidebar = document.querySelector('aside');
  if (!sidebar) return;

  // Create overlay
  const overlay = document.createElement('div');
  overlay.id = 'nav-overlay';
  overlay.className = 'fixed inset-0 bg-black/40 z-40 hidden md:hidden backdrop-blur-sm';
  overlay.addEventListener('click', closeMobileNav);
  document.body.appendChild(overlay);

  // Find or create hamburger button in header
  const menuBtn = document.querySelector('button.md\\:hidden') || (() => {
    const btn = document.createElement('button');
    btn.className = 'md:hidden text-primary p-2 rounded-lg hover:bg-surface-container transition-colors';
    btn.innerHTML = '<span class="material-symbols-outlined">menu</span>';
    const header = document.querySelector('header');
    if (header) header.prepend(btn);
    return btn;
  })();

  menuBtn.addEventListener('click', toggleMobileNav);

  function toggleMobileNav() {
    const isOpen = sidebar.classList.contains('translate-x-0');
    isOpen ? closeMobileNav() : openMobileNav();
  }

  function openMobileNav() {
    sidebar.classList.remove('hidden', '-translate-x-full');
    sidebar.classList.add('translate-x-0', 'flex');
    overlay.classList.remove('hidden');
    menuBtn.innerHTML = '<span class="material-symbols-outlined">close</span>';
  }

  function closeMobileNav() {
    sidebar.classList.remove('translate-x-0');
    sidebar.classList.add('-translate-x-full');
    overlay.classList.add('hidden');
    setTimeout(() => {
      if (!sidebar.classList.contains('md:flex')) {
        sidebar.classList.add('hidden');
        sidebar.classList.remove('-translate-x-full');
      }
    }, 300);
    menuBtn.innerHTML = '<span class="material-symbols-outlined">menu</span>';
  }

  // Add mobile transition classes to sidebar
  sidebar.classList.add('transition-transform', 'duration-300');

  // ── Replace avatar images with Flock logo ────────────────────────────────
  document.querySelectorAll('aside img, aside image').forEach(img => {
    const parent = img.parentElement;
    const logo = document.createElement('div');
    logo.className = 'w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-headline font-black text-base';
    logo.textContent = '🐦';
    parent.replaceChild(logo, img);
  });

})();
