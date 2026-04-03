/* NeuralFlow Docs — nav.js */

(function () {
  'use strict';

  /* ── Theme ───────────────────────────────────────────────────── */
  const THEME_KEY = 'nf-theme';

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const btn = document.getElementById('theme-btn');
    if (btn) btn.textContent = theme === 'dark' ? '☀️' : '🌙';
  }

  function initTheme() {
    const saved = localStorage.getItem(THEME_KEY) || 'dark';
    applyTheme(saved);
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    localStorage.setItem(THEME_KEY, next);
    applyTheme(next);
  }

  /* ── Mobile menu ─────────────────────────────────────────────── */
  function initMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const sidebar   = document.querySelector('.sidebar');
    if (!hamburger || !sidebar) return;

    hamburger.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', sidebar.classList.contains('open'));
    });

    document.addEventListener('click', (e) => {
      if (!sidebar.contains(e.target) && !hamburger.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  /* ── Active nav link ─────────────────────────────────────────── */
  function highlightActiveNav() {
    const path = window.location.pathname;
    document.querySelectorAll('.nav-links a, .sidebar-nav a').forEach((a) => {
      const href = a.getAttribute('href');
      if (!href) return;
      const abs = new URL(href, window.location.href).pathname;
      if (abs === path || (path.endsWith('/') && abs === path.slice(0, -1))) {
        a.classList.add('active');
      }
    });
  }

  /* ── Smooth scroll for same-page anchors ─────────────────────── */
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach((a) => {
      a.addEventListener('click', (e) => {
        const id = a.getAttribute('href').slice(1);
        const target = document.getElementById(id);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          history.pushState(null, '', '#' + id);
        }
      });
    });
  }

  /* ── Copy buttons for code blocks ────────────────────────────── */
  function initCopyButtons() {
    document.querySelectorAll('.code-wrap').forEach((wrap) => {
      const pre = wrap.querySelector('pre');
      if (!pre) return;
      const btn = wrap.querySelector('.copy-btn');
      if (!btn) return;

      btn.addEventListener('click', async () => {
        const text = pre.innerText || pre.textContent;
        try {
          await navigator.clipboard.writeText(text);
          btn.textContent = 'Copied!';
          btn.classList.add('copied');
          setTimeout(() => {
            btn.textContent = 'Copy';
            btn.classList.remove('copied');
          }, 2000);
        } catch {
          btn.textContent = 'Failed';
        }
      });
    });
  }

  /* ── Intersection-based sidebar scroll spy ───────────────────── */
  function initScrollSpy() {
    const sidebarLinks = document.querySelectorAll('.sidebar-nav a[href^="#"]');
    if (!sidebarLinks.length) return;

    const sections = [];
    sidebarLinks.forEach((a) => {
      const id = a.getAttribute('href').slice(1);
      const el = document.getElementById(id);
      if (el) sections.push({ el, a });
    });

    if (!sections.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            sidebarLinks.forEach((l) => l.classList.remove('active'));
            const match = sections.find((s) => s.el === entry.target);
            if (match) match.a.classList.add('active');
          }
        });
      },
      { rootMargin: '-20% 0px -70% 0px' }
    );

    sections.forEach(({ el }) => observer.observe(el));
  }

  /* ── Boot ────────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initMobileMenu();
    highlightActiveNav();
    initSmoothScroll();
    initCopyButtons();
    initScrollSpy();

    const themeBtn = document.getElementById('theme-btn');
    if (themeBtn) themeBtn.addEventListener('click', toggleTheme);
  });
})();
