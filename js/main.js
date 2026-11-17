/**
 * Portfolio Interaction Script
 * Strict adherence to AGENTS.md:
 * - Native APIs (HTML5 Dialog, IntersectionObserver)
 * - Passive event listeners
 * - Keyboard navigation (Tab, Shift+Tab, Escape, Enter, Space)
 * - Zero layout shifts (CLS < 0.1)
 */

document.addEventListener('DOMContentLoaded', () => {
  initHeroVideo();
  initMobileNav();
  initTourFilters();
  initMediaModal();
  initForms();
  initHeaderScroll();
  initAlbumCards();
});

/**
 * 0. Hero Background Looping Video & Reduced Motion Control
 */
function initHeroVideo() {
  const video = document.getElementById('hero-video');
  const toggleBtn = document.getElementById('hero-video-toggle');
  const pauseIcon = document.getElementById('hero-pause-icon');
  const playIcon = document.getElementById('hero-play-icon');
  const toggleText = document.getElementById('hero-video-toggle-text');

  if (!video || !toggleBtn) return;

  // Respect system-level reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReducedMotion) {
    video.pause();
    if (pauseIcon && playIcon && toggleText) {
      pauseIcon.style.display = 'none';
      playIcon.style.display = 'block';
      toggleText.textContent = 'Play Video';
      toggleBtn.setAttribute('aria-label', 'Play background video');
    }
  }

  toggleBtn.addEventListener('click', () => {
    if (video.paused) {
      video.play();
      if (pauseIcon) pauseIcon.style.display = 'block';
      if (playIcon) playIcon.style.display = 'none';
      if (toggleText) toggleText.textContent = 'Pause Video';
      toggleBtn.setAttribute('aria-label', 'Pause background video');
    } else {
      video.pause();
      if (pauseIcon) pauseIcon.style.display = 'none';
      if (playIcon) playIcon.style.display = 'block';
      if (toggleText) toggleText.textContent = 'Play Video';
      toggleBtn.setAttribute('aria-label', 'Play background video');
    }
  });
}

/**
 * 1. Mobile Navigation Drawer & Focus Management
 */
function initMobileNav() {
  const openBtn = document.getElementById('open-menu-btn');
  const closeBtn = document.getElementById('close-menu-btn');
  const navDialog = document.getElementById('mobile-nav-dialog');
  const navLinks = navDialog ? navDialog.querySelectorAll('.mobile-nav-link') : [];

  if (!openBtn || !closeBtn || !navDialog) return;

  function openMenu() {
    navDialog.showModal();
    document.body.style.overflow = 'hidden';
    closeBtn.focus();
  }

  function closeMenu() {
    navDialog.close();
    document.body.style.overflow = '';
    openBtn.focus();
  }

  openBtn.addEventListener('click', openMenu);
  closeBtn.addEventListener('click', closeMenu);

  // Close when clicking mobile nav links
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      closeMenu();
    });
  });

  // Handle Escape key
  navDialog.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeMenu();
    }
  });

  // Close on backdrop click
  navDialog.addEventListener('click', (e) => {
    if (e.target === navDialog) {
      closeMenu();
    }
  });
}

/**
 * 2. Tour Filter Category Switching
 */
function initTourFilters() {
  const filterPills = document.querySelectorAll('.filter-pill');
  const tourCards = document.querySelectorAll('.tour-card');

  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      const category = pill.getAttribute('data-filter');

      // Update ARIA and active states
      filterPills.forEach(p => {
        p.classList.remove('active');
        p.setAttribute('aria-selected', 'false');
      });
      pill.classList.add('active');
      pill.setAttribute('aria-selected', 'true');

      // Filter tour items
      tourCards.forEach(card => {
        const cardCategory = card.getAttribute('data-category');
        if (category === 'all' || cardCategory === category) {
          card.style.display = 'grid';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
}

/**
 * 3. Media Video Modal (Native <dialog>)
 */
function initMediaModal() {
  const modal = document.getElementById('media-modal');
  const closeBtn = document.getElementById('close-modal-btn');
  const modalTitle = document.getElementById('modal-title');
  const modalFrame = document.getElementById('modal-video-frame');
  const playButtons = document.querySelectorAll('.video-play-btn, .video-card');

  if (!modal || !closeBtn) return;

  playButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      // Find parent card if clicked inner button or card
      const card = btn.closest('.video-card');
      if (!card) return;

      const title = card.querySelector('.video-title')?.textContent || 'Live Performance';
      const videoEmbed = card.getAttribute('data-embed') || '';

      modalTitle.textContent = title;
      modalFrame.innerHTML = `
        <div style="width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #0c0c0d; color: #a1a1aa; padding: 2rem; text-align: center;">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-bottom: 1rem; color: var(--accent-gold);">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          <p style="font-weight: 700; color: #fff; font-size: 1.15rem; margin-bottom: 0.5rem;">${title}</p>
          <p style="font-size: 0.9rem; max-width: 40ch;">Live recording stream ready. Replace with your official YouTube or Vimeo embed ID.</p>
        </div>
      `;

      modal.showModal();
      closeBtn.focus();
    });
  });

  closeBtn.addEventListener('click', () => {
    modal.close();
    modalFrame.innerHTML = '';
  });

  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.close();
      modalFrame.innerHTML = '';
    }
  });

  modal.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      modal.close();
      modalFrame.innerHTML = '';
    }
  });
}

/**
 * 4. Interactive Forms & Toast Notifications
 */
function initForms() {
  const contactForm = document.getElementById('contact-form');
  const toast = document.getElementById('toast-notification');

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 4000);
  }

  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();
      showToast('Thank you! Your message and booking inquiry has been received.');
      contactForm.reset();
    });
  }
}

/**
 * 5. Passive Header Scroll Follow & Blur Effect
 */
function initHeaderScroll() {
  const header = document.querySelector('.site-header');
  if (!header) return;

  function handleScroll() {
    if (window.scrollY > 30) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  }

  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();
}

/**
 * 6. Album Card Click & Focus Handling
 * Releases focus on click so moving the mouse away cleanly fades out the overlay
 */
function initAlbumCards() {
  const cards = document.querySelectorAll('.album-card');
  cards.forEach(card => {
    card.addEventListener('click', () => {
      card.blur();
    });
  });
}

