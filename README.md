# Artist & Musician Portfolio Website

A modern, high-performance, accessible portfolio and live concert tour website engineered for artists, musicians, composers, and producers.

Inspired by and modeled directly on the design language of [robertglasper.com/#tour](https://robertglasper.com/#tour), with full compliance to the frontend, mobile ergonomics, and accessibility criteria in `AGENTS.md`.

---

## 🎹 Core Features & Blueprint Architecture

1. **Sticky Frosted-Glass Header & Accessible Mobile Drawer**:
   - High-contrast brand wordmark.
   - Smooth desktop link navigation (`#tour`, `#music`, `#videos`, `#about`, `#contact`).
   - Native HTML5 `<dialog>` mobile drawer with 48×48px tap targets, keyboard trap, and escape key handling.

2. **Full-Bleed Cinematic Hero (`#hero`)**:
   - Continuous looping video banner (`assets/mac_recap.mp4`) with dark cinematic vignette overlay.
   - Accessible Play/Pause toggle button complying with WCAG 2.1 AA (Guideline 2.2.2 Pause, Stop, Hide).
   - Automatic pause when `prefers-reduced-motion: reduce` is detected.
   - Accolade pill badges (e.g. *5× GRAMMY® Award Winner*).
   - High-impact display typography with fluid `clamp()` scaling.
   - Dual CTAs: *Explore Tour Dates* and *Stream Latest Music*.
   - Preloaded poster fallback (`assets/hero.svg`) ensuring instant LCP with zero layout shift.

3. **Live Tour & Residency Hub (`#tour`)**:
   - Filter bar: *All Dates*, *Blue Note Residency*, *World Tour*, *Festivals*.
   - Modular Tour Date Cards using CSS Container Queries (`@container tour (min-width: 720px)`):
     - Gold month header + bold date number + day of week.
     - City and Country.
     - Venue name and set info (e.g. *Robtober Residency 2026*, *With National Symphony Orchestra*).
     - Minimum 48px ticket buttons (*Tickets & VIP*, *Reserve Seats*, *Sold Out*).
   - Tour Tracking Box: "Don't see your city on the tour? Track Robert Glasper" with email notification signup.

4. **Discography & Releases Showcase (`#music`)**:
   - Dynamic responsive grid (3-col desktop, 2-col tablet, 1-col mobile).
   - Square 1:1 vinyl sleeve artwork with grooved textures and release badges.
   - Direct streaming actions (Spotify, Apple Music, Bandcamp, Vinyl orders).

5. **Video & Live Performance Archive (`#videos`)**:
   - 16:9 responsive video preview cards (NPR Tiny Desk, Orchestral Hall showcase, late-night jams).
   - Native `<dialog>` video modal with focus trapping and accessible controls.

6. **Editorial Biography & Accolades (`#about`)**:
   - Magazine-style split layout: portrait with quote overlay on the left, narrative biography and awards grid on the right.
   - Highlighting Grammy Awards, Peabody Award, Primetime Emmy, and Blue Note legacy.

7. **Direct Inquiry, Fan Club & Management (`#contact`)**:
   - Accessible form for booking, scoring commissions, press, and fan club inquiries.
   - Official representation cards for North America / Worldwide Booking (Wasserman Music), Artist Management (Vanguard), and Label / Sync (Blue Note Records).

8. **Footer & Social Links**:
   - Spotify, Apple Music, Instagram, and YouTube icon navigation.
   - WCAG 2.1 AA accessibility statement and back-to-top navigation.

---

## 🎨 Design Tokens & Customization

All theme variables are located at the top of `css/style.css`:

```css
:root {
  /* Color Palette */
  --bg-primary: #070707;          /* Pitch black canvas */
  --bg-secondary: #0f0f10;        /* Subtle contrast section background */
  --bg-surface: #151517;          /* Tour cards & music release containers */
  --accent-gold: #d4af37;         /* Warm metallic brass & gold accent */
  --text-primary: #f5f5f7;        /* Clean high-contrast typography */
  --text-secondary: #a1a1aa;      /* Subtitles & metadata */
  
  /* Typography Scale */
  --font-display: 'Syne', sans-serif;
  --font-body: 'Plus Jakarta Sans', sans-serif;
}
```

---

## 🚀 Getting Started & Local Preview

Run any local HTTP server in the project folder:

```bash
# Using Python
python3 -m http.server 3000

# Using Node / npx
npx serve .
```

Open `http://localhost:3000` in your browser.

---

## ♿ Accessibility & Performance Verification

- **Tap Targets**: Strict minimum of **48×48px** for all interactive elements with ≥ 8px spacing.
- **Focus States**: High-visibility `:focus-visible` styling (`outline: 2px solid var(--accent-gold); outline-offset: 4px;`).
- **Media Optimization**: Explicit `width` and `height` on all media to prevent Cumulative Layout Shift (CLS < 0.1).
- **Reduced Motion**: Full support for `@media (prefers-reduced-motion: reduce)`.
