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
  initPhotoCarousel();
  initSoundCloudPlayer();
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
    openBtn.setAttribute('aria-expanded', 'true');
    closeBtn.focus();
  }

  function closeMenu(restoreFocus = true) {
    if (!navDialog.open) return;
    navDialog.close();
    document.body.style.overflow = '';
    openBtn.setAttribute('aria-expanded', 'false');
    if (restoreFocus) {
      openBtn.focus({ preventScroll: true });
    }
  }

  openBtn.addEventListener('click', openMenu);
  closeBtn.addEventListener('click', () => closeMenu(true));

  // Close when clicking mobile nav links and jump to that section
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      const targetHash = link.getAttribute('href');
      closeMenu(false);

      if (targetHash && targetHash.startsWith('#')) {
        const targetElement = document.querySelector(targetHash);
        if (targetElement) {
          e.preventDefault();
          requestAnimationFrame(() => {
            targetElement.scrollIntoView({ behavior: 'smooth' });
            history.pushState(null, '', targetHash);
          });
        }
      }
    });
  });

  // Handle native cancel (Escape key)
  navDialog.addEventListener('cancel', (e) => {
    e.preventDefault();
    closeMenu(true);
  });

  // Close on backdrop click (clicking outside the side drawer)
  navDialog.addEventListener('click', (e) => {
    const rect = navDialog.getBoundingClientRect();
    const isInsideDrawer = (
      rect.top <= e.clientY &&
      e.clientY <= rect.top + rect.height &&
      rect.left <= e.clientX &&
      e.clientX <= rect.left + rect.width
    );
    if (!isInsideDrawer) {
      closeMenu(true);
    }
  });
}

/**
 * 2. Tour Filter Category Switching & Pagination (Max 8 Events per Page)
 */
function initTourFilters() {
  const emptyState = document.getElementById('tour-empty-state');
  const paginationNav = document.getElementById('tour-pagination');
  const prevBtn = document.getElementById('tour-page-prev');
  const nextBtn = document.getElementById('tour-page-next');
  const pageNumbersContainer = document.getElementById('tour-page-numbers');
  const sortSelect = document.getElementById('tour-sort-select');
  const tourList = document.querySelector('.tour-list');
  const filterBar = document.querySelector('.tour-filter-bar');

  const PAGE_SIZE = 8;
  let currentCategory = 'all';
  let currentPage = 1;
  let currentSort = sortSelect ? sortSelect.value : 'asc';

  function updateDisplay(scrollOnChange = false) {
    // 1. Determine cards matching active category
    const currentCards = document.querySelectorAll('.tour-card');
    const matchingCards = [];
    currentCards.forEach(card => {
      const cardCategory = card.getAttribute('data-category');
      if (currentCategory === 'all' || cardCategory === currentCategory) {
        matchingCards.push(card);
      }
    });

    const totalMatching = matchingCards.length;

    // 2. Handle 0 matching events (Empty State)
    if (totalMatching === 0) {
      currentCards.forEach(card => { card.style.display = 'none'; });
      if (emptyState) emptyState.style.display = 'flex';
      if (paginationNav) paginationNav.style.display = 'none';
      return;
    }

    // Hide empty state if we have matching events
    if (emptyState) emptyState.style.display = 'none';

    // 3. Sort matching cards by date based on currentSort ('asc' vs 'desc')
    matchingCards.sort((a, b) => {
      const dateA = new Date(a.getAttribute('data-date') || 0).getTime();
      const dateB = new Date(b.getAttribute('data-date') || 0).getTime();
      return currentSort === 'desc' ? (dateB - dateA) : (dateA - dateB);
    });

    // Reorder matching cards in the DOM list
    if (tourList) {
      matchingCards.forEach(card => tourList.appendChild(card));
    }

    // 4. Calculate pagination
    const totalPages = Math.ceil(totalMatching / PAGE_SIZE);
    if (currentPage > totalPages) {
      currentPage = 1;
    }

    const startIndex = (currentPage - 1) * PAGE_SIZE;
    const endIndex = startIndex + PAGE_SIZE;

    // 5. Update card visibility
    currentCards.forEach(card => {
      card.style.display = 'none';
    });

    matchingCards.forEach((card, index) => {
      if (index >= startIndex && index < endIndex) {
        card.style.display = 'grid';
      } else {
        card.style.display = 'none';
      }
    });

    // 6. Update pagination UI (show only if > 8 items)
    if (totalPages <= 1) {
      if (paginationNav) paginationNav.style.display = 'none';
    } else {
      if (paginationNav) {
        paginationNav.style.display = 'flex';

        // Update Prev / Next buttons
        if (prevBtn) {
          prevBtn.disabled = (currentPage === 1);
        }
        if (nextBtn) {
          nextBtn.disabled = (currentPage === totalPages);
        }

        // Render page numbers
        if (pageNumbersContainer) {
          pageNumbersContainer.innerHTML = '';
          for (let p = 1; p <= totalPages; p++) {
            const pageBtn = document.createElement('button');
            pageBtn.type = 'button';
            pageBtn.className = 'tour-page-num' + (p === currentPage ? ' active' : '');
            pageBtn.textContent = p;
            pageBtn.setAttribute('aria-label', 'Page ' + p);
            if (p === currentPage) {
              pageBtn.setAttribute('aria-current', 'page');
            }
            pageBtn.addEventListener('click', () => {
              if (currentPage !== p) {
                currentPage = p;
                updateDisplay(true);
              }
            });
            pageNumbersContainer.appendChild(pageBtn);
          }
        }
      }
    }

    // 7. Smooth scroll to tour heading on page change if requested
    if (scrollOnChange) {
      const tourHeading = document.getElementById('tour-heading');
      if (tourHeading) {
        const yOffset = -90;
        const y = tourHeading.getBoundingClientRect().top + window.pageYOffset + yOffset;
        window.scrollTo({ top: y, behavior: 'smooth' });
      }
    }
  }

  // Sort dropdown change listener
  if (sortSelect) {
    sortSelect.addEventListener('change', () => {
      currentSort = sortSelect.value;
      currentPage = 1;
      updateDisplay(false);
    });
  }

  // Previous button handler
  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (currentPage > 1) {
        currentPage--;
        updateDisplay(true);
      }
    });
  }

  // Next button handler
  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      const currentCards = document.querySelectorAll('.tour-card');
      const matchingCount = Array.from(currentCards).filter(c => {
        const cat = c.getAttribute('data-category');
        return currentCategory === 'all' || cat === currentCategory;
      }).length;
      const totalPages = Math.ceil(matchingCount / PAGE_SIZE);
      if (currentPage < totalPages) {
        currentPage++;
        updateDisplay(true);
      }
    });
  }

  // Filter Pill buttons (event delegation on container for dynamic region tabs + swipe/drag)
  if (filterBar) {
    let isDown = false;
    let startX = 0;
    let scrollStart = 0;
    let dragged = false;

    // Desktop mousewheel horizontal scrolling support
    filterBar.addEventListener('wheel', (e) => {
      if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
        filterBar.scrollLeft += e.deltaY;
        e.preventDefault();
      }
    }, { passive: false });

    filterBar.addEventListener('mousedown', (e) => {
      isDown = true;
      dragged = false;
      startX = e.pageX - filterBar.offsetLeft;
      scrollStart = filterBar.scrollLeft;
      filterBar.style.cursor = 'grabbing';
    });

    window.addEventListener('mouseup', () => {
      if (isDown) {
        isDown = false;
        if (filterBar) filterBar.style.cursor = '';
      }
    });

    filterBar.addEventListener('mousemove', (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - filterBar.offsetLeft;
      const walk = (x - startX);
      if (Math.abs(walk) > 5) {
        dragged = true;
      }
      filterBar.scrollLeft = scrollStart - walk;
    });

    filterBar.addEventListener('click', (e) => {
      if (dragged) {
        dragged = false;
        return;
      }
      const pill = e.target.closest('.filter-pill');
      if (!pill) return;

      currentCategory = pill.getAttribute('data-filter') || 'all';
      currentPage = 1;

      // Update ARIA and active states
      const allPills = filterBar.querySelectorAll('.filter-pill');
      allPills.forEach(p => {
        p.classList.remove('active');
        p.setAttribute('aria-selected', 'false');
      });
      pill.classList.add('active');
      pill.setAttribute('aria-selected', 'true');

      // Scroll active pill cleanly into view when overflowing
      pill.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });

      updateDisplay(false);
    });
  }

  // Initial setup run
  updateDisplay(false);
}

/**
 * Helper to detect mobile device viewports & touch capabilities
 */
function isMobileDevice() {
  const ua = navigator.userAgent || '';
  const isMobileUA = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua);
  const isTouchScreen = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
  const isNarrow = window.innerWidth <= 820;
  return isMobileUA || (isTouchScreen && isNarrow);
}

/**
 * 3. Media Video Modal (Native <dialog>)
 */
function initMediaModal() {
  const modal = document.getElementById('media-modal');
  const closeBtn = document.getElementById('close-modal-btn');
  const modalTitle = document.getElementById('modal-title');
  const modalFrame = document.getElementById('modal-video-frame');
  const modalYoutubeBtn = document.getElementById('modal-youtube-btn');
  const modalFallbackLink = document.getElementById('modal-fallback-link');
  const playButtons = document.querySelectorAll('.video-play-btn, .video-card');

  if (!modal || !closeBtn) return;

  let currentVideoId = '';
  let currentTitle = '';
  let currentYtUrl = '';

  function openYouTubeDirectly(url) {
    const targetWin = window.open(url, '_blank');
    if (!targetWin) {
      window.location.href = url;
    }
  }

  function showErrorFallback(title, ytUrl) {
    modalFrame.innerHTML = `
      <div style="width: 100%; min-height: 340px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #0c0c0d; padding: 2rem; text-align: center; border-radius: 8px;">
        <div style="width: 60px; height: 60px; border-radius: 50%; background: rgba(255, 0, 0, 0.12); color: #ff0000; display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
            <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
          </svg>
        </div>
        <p style="font-weight: 700; color: #fff; font-size: 1.2rem; margin-bottom: 0.5rem;">${title}</p>
        <p style="font-size: 0.95rem; color: #a1a1aa; max-width: 44ch; margin-bottom: 1.5rem; line-height: 1.4;">
          This broadcast performance has embedded playback restrictions. Open directly in the YouTube app for uninterrupted full-quality viewing.
        </p>
        <a href="${ytUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="display: inline-flex; align-items: center; gap: 8px; background: #ff0000; border-color: #ff0000; color: #fff; min-height: 48px; padding: 0.75rem 1.75rem; font-weight: 700; text-transform: uppercase;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
          </svg>
          Open in YouTube App
        </a>
      </div>
    `;
  }

  function handleVideoActivation(card) {
    currentTitle = card.querySelector('.video-title')?.textContent || 'Live Performance';
    currentVideoId = card.getAttribute('data-embed') || '';
    currentYtUrl = card.getAttribute('data-youtube-url') || `https://www.youtube.com/watch?v=${encodeURIComponent(currentVideoId)}`;

    // On mobile devices, YouTube restricts 3rd-party embedded playback for TV broadcasts (Kimmel, MTV).
    // Launch directly in the YouTube app for native full-screen playback.
    if (isMobileDevice()) {
      openYouTubeDirectly(currentYtUrl);
      return;
    }

    // On desktop / large viewports, open the native dialog player
    modalTitle.textContent = currentTitle;
    if (modalYoutubeBtn) {
      modalYoutubeBtn.href = currentYtUrl;
    }
    if (modalFallbackLink) {
      modalFallbackLink.href = currentYtUrl;
    }

    if (currentVideoId && currentVideoId.length === 11) {
      modalFrame.innerHTML = `
        <iframe 
          id="active-youtube-iframe"
          src="https://www.youtube-nocookie.com/embed/${encodeURIComponent(currentVideoId)}?autoplay=1&rel=0&enablejsapi=1" 
          title="${currentTitle.replace(/"/g, '&quot;')}" 
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
          allowfullscreen
          style="width: 100%; height: 100%; min-height: 380px; border: none; aspect-ratio: 16/9; border-radius: 8px;"
        ></iframe>
      `;
    } else {
      showErrorFallback(currentTitle, currentYtUrl);
    }

    modal.showModal();
    closeBtn.focus();
  }

  // Listen for YouTube postMessage errors (e.g. error 101, 150 = embedded playback disallowed)
  window.addEventListener('message', (e) => {
    try {
      const data = typeof e.data === 'string' ? JSON.parse(e.data) : e.data;
      if (data && (data.event === 'onError' || (data.info && typeof data.info === 'number' && [2, 5, 100, 101, 150].includes(data.info)))) {
        showErrorFallback(currentTitle, currentYtUrl);
        if (isMobileDevice()) {
          openYouTubeDirectly(currentYtUrl);
        }
      }
    } catch (err) {}
  });

  playButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const card = btn.closest('.video-card');
      if (!card) return;
      handleVideoActivation(card);
    });

    // Keyboard activation for card elements with role="button"
    if (btn.classList.contains('video-card')) {
      btn.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleVideoActivation(btn);
        }
      });
    }
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

/**
 * 7. Tour & Stage Photo Carousel / Slideshow & Lightbox
 */
function initPhotoCarousel() {
  const stage = document.getElementById('carousel-3d-stage');
  const prevBtn = document.getElementById('carousel-3d-prev');
  const nextBtn = document.getElementById('carousel-3d-next');
  const items = Array.from(document.querySelectorAll('.carousel-3d-item'));

  const lightbox = document.getElementById('photo-lightbox-modal');
  const lightboxImg = document.getElementById('lightbox-img');
  const lightboxCaption = document.getElementById('lightbox-caption');
  const lightboxCounter = document.getElementById('lightbox-counter');
  const closeLightboxBtn = document.getElementById('close-lightbox-btn');
  const lightboxPrevBtn = document.getElementById('lightbox-prev-btn');
  const lightboxNextBtn = document.getElementById('lightbox-next-btn');

  if (!stage || items.length === 0) return;

  const total = items.length;
  let activeIdx = 0;
  let autoplayTimer = null;
  const isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function formatIndex(idx) {
    return String(idx + 1).padStart(2, '0');
  }

  function getResponsiveParams() {
    const w = window.innerWidth;
    if (w <= 480) {
      return { step1: 44, step2: 78, step3: 105, scale1: 0.82, scale2: 0.68, scale3: 0.54, z1: -60, z2: -120, z3: -180 };
    } else if (w <= 768) {
      return { step1: 90, step2: 165, step3: 230, scale1: 0.85, scale2: 0.72, scale3: 0.58, z1: -70, z2: -140, z3: -210 };
    } else if (w <= 1024) {
      return { step1: 135, step2: 250, step3: 345, scale1: 0.86, scale2: 0.73, scale3: 0.60, z1: -80, z2: -160, z3: -240 };
    } else {
      return { step1: 175, step2: 320, step3: 435, scale1: 0.88, scale2: 0.75, scale3: 0.62, z1: -90, z2: -180, z3: -270 };
    }
  }

  function update3DCarousel() {
    const p = getResponsiveParams();
    items.forEach((item, idx) => {
      let offset = (idx - activeIdx + total) % total;
      if (offset > total / 2) offset -= total;

      const isActive = offset === 0;
      item.classList.toggle('active', isActive);

      if (isActive) {
        item.style.transform = 'translate3d(-50%, -50%, 0) scale(1)';
        item.style.zIndex = '10';
        item.style.opacity = '1';
        item.style.pointerEvents = 'auto';
        item.setAttribute('aria-hidden', 'false');
        item.setAttribute('tabindex', '0');
      } else if (Math.abs(offset) === 1) {
        const sign = offset > 0 ? 1 : -1;
        item.style.transform = `translate3d(calc(-50% + ${sign * p.step1}px), -50%, ${p.z1}px) scale(${p.scale1})`;
        item.style.zIndex = '8';
        item.style.opacity = '0.88';
        item.style.pointerEvents = 'auto';
        item.setAttribute('aria-hidden', 'false');
        item.setAttribute('tabindex', '0');
      } else if (Math.abs(offset) === 2) {
        const sign = offset > 0 ? 1 : -1;
        item.style.transform = `translate3d(calc(-50% + ${sign * p.step2}px), -50%, ${p.z2}px) scale(${p.scale2})`;
        item.style.zIndex = '6';
        item.style.opacity = '0.70';
        item.style.pointerEvents = 'auto';
        item.setAttribute('aria-hidden', 'false');
        item.setAttribute('tabindex', '0');
      } else if (Math.abs(offset) === 3) {
        const sign = offset > 0 ? 1 : -1;
        item.style.transform = `translate3d(calc(-50% + ${sign * p.step3}px), -50%, ${p.z3}px) scale(${p.scale3})`;
        item.style.zIndex = '4';
        item.style.opacity = '0.45';
        item.style.pointerEvents = 'auto';
        item.setAttribute('aria-hidden', 'false');
        item.setAttribute('tabindex', '0');
      } else {
        const sign = offset > 0 ? 1 : -1;
        item.style.transform = `translate3d(calc(-50% + ${sign * (p.step3 + 80)}px), -50%, -360px) scale(0.38)`;
        item.style.zIndex = '0';
        item.style.opacity = '0';
        item.style.pointerEvents = 'none';
        item.setAttribute('aria-hidden', 'true');
        item.setAttribute('tabindex', '-1');
      }
    });
  }

  function prevSlide() {
    pauseAutoplay();
    activeIdx = (activeIdx - 1 + total) % total;
    update3DCarousel();
  }

  function nextSlide() {
    pauseAutoplay();
    activeIdx = (activeIdx + 1) % total;
    update3DCarousel();
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', prevSlide);
  }
  if (nextBtn) {
    nextBtn.addEventListener('click', nextSlide);
  }

  // Card interaction: side card brings to center, center card opens full lightbox
  items.forEach((item, idx) => {
    item.addEventListener('click', () => {
      if (activeIdx !== idx) {
        pauseAutoplay();
        activeIdx = idx;
        update3DCarousel();
      } else {
        openLightbox(idx);
      }
    });

    item.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        if (activeIdx !== idx) {
          pauseAutoplay();
          activeIdx = idx;
          update3DCarousel();
        } else {
          openLightbox(idx);
        }
      }
    });
  });

  // Stage keyboard navigation
  stage.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      prevSlide();
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      nextSlide();
    }
  });

  // Touch swipe support on stage
  let touchStartX = 0;
  let touchEndX = 0;
  stage.addEventListener('touchstart', (e) => {
    pauseAutoplay();
    touchStartX = e.changedTouches[0].clientX;
  }, { passive: true });

  stage.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].clientX;
    const diff = touchEndX - touchStartX;
    if (Math.abs(diff) > 40) {
      if (diff > 0) {
        prevSlide();
      } else {
        nextSlide();
      }
    }
  }, { passive: true });

  // Responsive repositioning on resize
  window.addEventListener('resize', () => {
    update3DCarousel();
  }, { passive: true });

  // Autoplay
  function startAutoplay() {
    if (isReducedMotion || autoplayTimer) return;
    autoplayTimer = setInterval(nextSlide, 5000);
  }

  function pauseAutoplay() {
    if (autoplayTimer) {
      clearInterval(autoplayTimer);
      autoplayTimer = null;
    }
  }

  stage.addEventListener('mouseenter', pauseAutoplay);
  stage.addEventListener('mouseleave', startAutoplay);
  stage.addEventListener('focusin', pauseAutoplay);
  stage.addEventListener('focusout', startAutoplay);
  startAutoplay();

  // Lightbox Implementation
  let activeLightboxIdx = 0;

  function openLightbox(idx) {
    if (!lightbox || !lightboxImg) return;
    pauseAutoplay();
    activeLightboxIdx = Math.max(0, Math.min(total - 1, idx));
    const item = items[activeLightboxIdx];
    if (!item) return;

    const img = item.querySelector('.carousel-3d-img');
    const src = img ? (img.currentSrc || img.src) : '';
    const alt = img ? img.alt : '';

    lightboxImg.src = src;
    lightboxImg.alt = alt;
    if (lightboxCaption) {
      lightboxCaption.textContent = alt || `Tour Photo ${formatIndex(activeLightboxIdx)}`;
    }
    if (lightboxCounter) {
      lightboxCounter.textContent = `${formatIndex(activeLightboxIdx)} / ${formatIndex(total - 1)}`;
    }

    lightbox.showModal();
    if (closeLightboxBtn) closeLightboxBtn.focus();
  }

  function closeLightbox() {
    if (!lightbox || !lightbox.open) return;
    lightbox.close();
    if (lightboxImg) lightboxImg.src = '';
  }

  if (closeLightboxBtn) {
    closeLightboxBtn.addEventListener('click', closeLightbox);
  }

  if (lightboxPrevBtn) {
    lightboxPrevBtn.addEventListener('click', () => {
      const prev = activeLightboxIdx > 0 ? activeLightboxIdx - 1 : total - 1;
      openLightbox(prev);
    });
  }

  if (lightboxNextBtn) {
    lightboxNextBtn.addEventListener('click', () => {
      const next = activeLightboxIdx < total - 1 ? activeLightboxIdx + 1 : 0;
      openLightbox(next);
    });
  }

  if (lightbox) {
    lightbox.addEventListener('click', (e) => {
      const rect = lightbox.getBoundingClientRect();
      const isInside = (
        rect.top <= e.clientY &&
        e.clientY <= rect.top + rect.height &&
        rect.left <= e.clientX &&
        e.clientX <= rect.left + rect.width
      );
      if (!isInside) {
        closeLightbox();
      }
    });

    lightbox.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeLightbox();
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        const prev = activeLightboxIdx > 0 ? activeLightboxIdx - 1 : total - 1;
        openLightbox(prev);
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        const next = activeLightboxIdx < total - 1 ? activeLightboxIdx + 1 : 0;
        openLightbox(next);
      }
    });
  }

  // Initial layout calculation
  update3DCarousel();
}

/**
 * 8. SoundCloud Audio Track Player (Search-Result Track Style)
 */
function initSoundCloudPlayer() {
  const playBtn = document.getElementById('sc-play-toggle-btn');
  const playIcon = document.getElementById('sc-play-icon');
  const pauseIcon = document.getElementById('sc-pause-icon');
  const barsContainer = document.getElementById('sc-waveform-bars');
  const playhead = document.getElementById('sc-playhead');
  const waveformWrap = document.getElementById('sc-waveform');
  const currentTimeEl = document.getElementById('sc-current-time');
  const totalTimeEl = document.getElementById('sc-total-time');
  const widgetIframe = document.getElementById('sc-hidden-widget');

  if (!playBtn || !barsContainer) return;

  // Waveform Bar Heights Generation (SoundCloud audio peak profile)
  const barHeights = [
    20, 28, 38, 52, 68, 48, 35, 55, 75, 92, 80, 62, 45, 65, 82,
    95, 88, 70, 54, 40, 58, 78, 92, 85, 68, 50, 42, 60, 78, 90,
    82, 65, 48, 36, 52, 70, 84, 75, 60, 46, 34, 45, 30, 20, 14
  ];

  const barElements = [];
  barsContainer.innerHTML = '';
  barHeights.forEach((h) => {
    const bar = document.createElement('span');
    bar.className = 'sc-bar';
    bar.style.height = `${h}%`;
    barsContainer.appendChild(bar);
    barElements.push(bar);
  });

  function formatTime(seconds) {
    const s = Math.floor(seconds || 0);
    const m = Math.floor(s / 60);
    const rem = s % 60;
    return `${m}:${String(rem).padStart(2, '0')}`;
  }

  let durationSec = 319.11; // 5:19 default track duration
  let isPlaying = false;
  let widget = null;

  function updateProgress(fraction, currentSec) {
    const clamped = Math.max(0, Math.min(1, fraction));
    if (playhead) playhead.style.left = `${clamped * 100}%`;
    if (waveformWrap) waveformWrap.setAttribute('aria-valuenow', Math.floor(currentSec));
    if (currentTimeEl) currentTimeEl.textContent = formatTime(currentSec);

    const playedCount = Math.floor(clamped * barElements.length);
    barElements.forEach((bar, idx) => {
      bar.classList.toggle('played', idx < playedCount);
    });
  }

  function setPlayState(playing) {
    isPlaying = playing;
    if (playIcon) playIcon.style.display = playing ? 'none' : 'block';
    if (pauseIcon) pauseIcon.style.display = playing ? 'block' : 'none';
    if (playBtn) playBtn.setAttribute('aria-label', playing ? 'Pause Naïka Richard - Papa Gede' : 'Play Naïka Richard - Papa Gede');
  }

  // Initialize SoundCloud Widget API if available
  if (typeof SC !== 'undefined' && widgetIframe) {
    try {
      widget = SC.Widget(widgetIframe);

      widget.bind(SC.Widget.Events.READY, () => {
        widget.getDuration((ms) => {
          if (ms > 0) {
            durationSec = ms / 1000;
            if (totalTimeEl) totalTimeEl.textContent = formatTime(durationSec);
            if (waveformWrap) waveformWrap.setAttribute('aria-valuemax', Math.floor(durationSec));
          }
        });
      });

      widget.bind(SC.Widget.Events.PLAY, () => setPlayState(true));
      widget.bind(SC.Widget.Events.PAUSE, () => setPlayState(false));
      widget.bind(SC.Widget.Events.FINISH, () => {
        setPlayState(false);
        updateProgress(0, 0);
      });

      widget.bind(SC.Widget.Events.PLAY_PROGRESS, (data) => {
        const currentSec = (data.currentPosition || 0) / 1000;
        const frac = data.relativePosition != null ? data.relativePosition : (currentSec / durationSec);
        updateProgress(frac, currentSec);
      });
    } catch (e) {
      console.warn('SoundCloud Widget error:', e);
    }
  }

  if (playBtn) {
    playBtn.addEventListener('click', () => {
      if (widget) {
        widget.toggle();
      } else {
        setPlayState(!isPlaying);
      }
    });
  }

  function seekByFraction(frac) {
    const targetSec = durationSec * frac;
    updateProgress(frac, targetSec);
    if (widget) {
      widget.seekTo(targetSec * 1000);
      if (!isPlaying) widget.play();
    }
  }

  if (waveformWrap) {
    waveformWrap.addEventListener('click', (e) => {
      const rect = waveformWrap.getBoundingClientRect();
      const frac = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
      seekByFraction(frac);
    });

    waveformWrap.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        const currentSec = parseFloat(waveformWrap.getAttribute('aria-valuenow')) || 0;
        seekByFraction(Math.max(0, (currentSec - 5) / durationSec));
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        const currentSec = parseFloat(waveformWrap.getAttribute('aria-valuenow')) || 0;
        seekByFraction(Math.min(1, (currentSec + 5) / durationSec));
      } else if (e.key === ' ' || e.key === 'Enter') {
        e.preventDefault();
        if (widget) widget.toggle();
        else setPlayState(!isPlaying);
      }
    });
  }
}

