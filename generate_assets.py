import os

os.makedirs('assets', exist_ok=True)

# 1. Hero Artwork (Cinematic piano / stage ambient noir)
hero_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="100%" height="100%">
  <defs>
    <radialGradient id="stageLight" cx="40%" cy="30%" r="70%">
      <stop offset="0%" stop-color="#3a2e1d" stop-opacity="0.8"/>
      <stop offset="40%" stop-color="#141416" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#070707" stop-opacity="1"/>
    </radialGradient>
    <linearGradient id="goldBeam" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#d4af37" stop-opacity="0.25"/>
      <stop offset="50%" stop-color="#d4af37" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="transparent" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="pianoGloss" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#2a2a2e"/>
      <stop offset="100%" stop-color="#0a0a0c"/>
    </linearGradient>
  </defs>
  
  <!-- Ambient backdrop -->
  <rect width="1920" height="1080" fill="url(#stageLight)"/>
  
  <!-- Atmospheric stage light cones -->
  <polygon points="500,0 200,1080 850,1080" fill="url(#goldBeam)"/>
  <polygon points="1200,0 950,1080 1500,1080" fill="url(#goldBeam)" opacity="0.6"/>
  
  <!-- Grand Piano silhouette & Stage floor -->
  <ellipse cx="960" cy="980" rx="900" ry="240" fill="#0c0c0e" opacity="0.9"/>
  
  <!-- Stylized Steinway Grand Outline -->
  <path d="M 680,680 Q 780,520 1050,530 T 1380,650 L 1400,750 L 660,750 Z" fill="url(#pianoGloss)" stroke="#38383f" stroke-width="2"/>
  <rect x="680" y="740" width="700" height="18" fill="#18181b" stroke="#d4af37" stroke-width="1" opacity="0.6"/>
  
  <!-- Piano Keys (Subtle warm highlight) -->
  <g opacity="0.7">
    <!-- Key pattern representation -->
    <rect x="720" y="742" width="620" height="12" fill="#e4e4e7"/>
    <rect x="740" y="742" width="12" height="7" fill="#09090b"/>
    <rect x="760" y="742" width="12" height="7" fill="#09090b"/>
    <rect x="790" y="742" width="12" height="7" fill="#09090b"/>
    <rect x="810" y="742" width="12" height="7" fill="#09090b"/>
    <rect x="830" y="742" width="12" height="7" fill="#09090b"/>
    <rect x="860" y="742" width="12" height="7" fill="#09090b"/>
    <rect x="880" y="742" width="12" height="7" fill="#09090b"/>
    <rect x="910" y="742" width="12" height="7" fill="#09090b"/>
    <rect x="930" y="742" width="12" height="7" fill="#09090b"/>
    <rect x="950" y="742" width="12" height="7" fill="#09090b"/>
  </g>

  <!-- Atmospheric micro-particles / stage dust -->
  <circle cx="650" cy="420" r="2" fill="#d4af37" opacity="0.6"/>
  <circle cx="820" cy="310" r="1.5" fill="#ffffff" opacity="0.5"/>
  <circle cx="1120" cy="480" r="2.5" fill="#d4af37" opacity="0.4"/>
  <circle cx="1290" cy="360" r="1.5" fill="#ffffff" opacity="0.7"/>
</svg>'''

with open('assets/hero.svg', 'w') as f:
    f.write(hero_svg)

# 2. Bio Editorial Portrait
bio_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000" width="100%" height="100%">
  <defs>
    <linearGradient id="bioGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1c1917"/>
      <stop offset="50%" stop-color="#141416"/>
      <stop offset="100%" stop-color="#070707"/>
    </linearGradient>
    <radialGradient id="portraitGlow" cx="50%" cy="40%" r="50%">
      <stop offset="0%" stop-color="#d4af37" stop-opacity="0.2"/>
      <stop offset="100%" stop-color="transparent" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="800" height="1000" fill="url(#bioGrad)"/>
  <circle cx="400" cy="380" r="280" fill="url(#portraitGlow)"/>
  
  <!-- Stylized artist silhouette / profile -->
  <path d="M 400,240 C 330,240 280,290 280,380 C 280,480 340,540 400,540 C 460,540 520,480 520,380 C 520,290 470,240 400,240 Z" fill="#26262a" opacity="0.85"/>
  <!-- Headphone silhouette -->
  <path d="M 270,360 Q 400,210 530,360" stroke="#d4af37" stroke-width="8" fill="none" opacity="0.8"/>
  <rect x="255" y="350" width="30" height="60" rx="15" fill="#d4af37" opacity="0.85"/>
  <rect x="515" y="350" width="30" height="60" rx="15" fill="#d4af37" opacity="0.85"/>

  <!-- Shoulders & studio torso -->
  <path d="M 180,950 Q 200,600 400,600 Q 600,600 620,950 Z" fill="#18181b"/>
  
  <!-- Acoustic wave lines -->
  <g opacity="0.15" stroke="#d4af37" stroke-width="2">
    <line x1="80" y1="820" x2="720" y2="820"/>
    <line x1="120" y1="840" x2="680" y2="840"/>
    <line x1="160" y1="860" x2="640" y2="860"/>
  </g>
</svg>'''

with open('assets/bio.svg', 'w') as f:
    f.write(bio_svg)

# 3. Album Artworks
albums = [
    ("Black Radio III", "Deluxe Edition", "#d4af37", "#1a1505"),
    ("Blue Note Live", "The October Sessions", "#38bdf8", "#081b26"),
    ("Echoes of Tomorrow", "Original Master", "#c084fc", "#1a0b26"),
    ("Dinner Party", "Continuum EP", "#f43f5e", "#240810"),
    ("Acoustic Trio", "Live in Tokyo", "#fbbf24", "#241805"),
    ("Milestones", "A Retrospective", "#34d399", "#062114")
]

for idx, (title, sub, accent, bg) in enumerate(albums, 1):
    album_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="100%" height="100%">
  <defs>
    <radialGradient id="vinylRings" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{bg}"/>
      <stop offset="90%" stop-color="#0a0a0c"/>
      <stop offset="100%" stop-color="#000000"/>
    </radialGradient>
  </defs>
  <rect width="600" height="600" fill="url(#vinylRings)"/>
  
  <!-- Subtle vinyl grooves -->
  <circle cx="300" cy="300" r="260" stroke="#ffffff" stroke-width="0.5" fill="none" opacity="0.1"/>
  <circle cx="300" cy="300" r="220" stroke="#ffffff" stroke-width="0.5" fill="none" opacity="0.08"/>
  <circle cx="300" cy="300" r="180" stroke="#ffffff" stroke-width="0.5" fill="none" opacity="0.08"/>
  <circle cx="300" cy="300" r="140" stroke="#ffffff" stroke-width="0.5" fill="none" opacity="0.1"/>

  <!-- Center Label -->
  <circle cx="300" cy="300" r="95" fill="#141417" stroke="{accent}" stroke-width="2"/>
  <circle cx="300" cy="300" r="15" fill="#000" stroke="#52525b" stroke-width="1.5"/>

  <!-- Typography on Cover -->
  <text x="40" y="90" font-family="'Syne', sans-serif" font-size="34" font-weight="800" fill="#ffffff" letter-spacing="-0.02em">{title.upper()}</text>
  <text x="42" y="125" font-family="'Plus Jakarta Sans', sans-serif" font-size="14" font-weight="700" fill="{accent}" letter-spacing="0.15em">{sub.upper()}</text>
  
  <!-- Bottom serial mark -->
  <text x="40" y="550" font-family="monospace" font-size="12" fill="#71717a" letter-spacing="0.1em">BLUE NOTE RECORDS // STEREO LP-{idx:02d}0{idx*3}</text>
</svg>'''
    with open(f'assets/album{idx}.svg', 'w') as f:
        f.write(album_svg)

# 4. Video Thumbnails
videos = [
    ("Tiny Desk Concert", "NPR Music Live Session", "#d4af37"),
    ("Live at Symphony Hall", "With BBC Concert Orchestra", "#38bdf8"),
    ("Late Night Blue Note Jam", "Feat. Special Guests", "#c084fc"),
    ("The Making of Black Radio", "Studio Documentary", "#f43f5e")
]

for idx, (title, sub, accent) in enumerate(videos, 1):
    video_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="100%" height="100%">
  <defs>
    <linearGradient id="vidGrad{idx}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#18181b"/>
      <stop offset="50%" stop-color="#0f0f11"/>
      <stop offset="100%" stop-color="#060607"/>
    </linearGradient>
    <radialGradient id="stageSpot{idx}" cx="50%" cy="40%" r="55%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="transparent" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1280" height="720" fill="url(#vidGrad{idx})"/>
  <circle cx="640" cy="340" r="400" fill="url(#stageSpot{idx})"/>
  
  <!-- Visual Sound Wave / Equilizer Graphic -->
  <g opacity="0.3" fill="{accent}">
    <rect x="240" y="440" width="20" height="60" rx="4"/>
    <rect x="280" y="380" width="20" height="120" rx="4"/>
    <rect x="320" y="320" width="20" height="180" rx="4"/>
    <rect x="360" y="400" width="20" height="100" rx="4"/>
    <rect x="400" y="350" width="20" height="150" rx="4"/>
    <rect x="440" y="280" width="20" height="220" rx="4"/>
    <rect x="480" y="360" width="20" height="140" rx="4"/>
    
    <rect x="780" y="360" width="20" height="140" rx="4"/>
    <rect x="820" y="280" width="20" height="220" rx="4"/>
    <rect x="860" y="350" width="20" height="150" rx="4"/>
    <rect x="900" y="400" width="20" height="100" rx="4"/>
    <rect x="940" y="320" width="20" height="180" rx="4"/>
    <rect x="980" y="380" width="20" height="120" rx="4"/>
    <rect x="1020" y="440" width="20" height="60" rx="4"/>
  </g>

  <!-- Live Tag -->
  <rect x="60" y="60" width="80" height="28" rx="6" fill="#dc2626"/>
  <text x="100" y="79" font-family="sans-serif" font-size="12" font-weight="800" fill="#ffffff" text-anchor="middle" letter-spacing="0.1em">LIVE</text>
  
  <text x="60" y="640" font-family="'Syne', sans-serif" font-size="36" font-weight="800" fill="#ffffff">{title.upper()}</text>
  <text x="60" y="675" font-family="'Plus Jakarta Sans', sans-serif" font-size="16" font-weight="600" fill="{accent}">{sub}</text>
</svg>'''
    with open(f'assets/video{idx}.svg', 'w') as f:
        f.write(video_svg)

print("Assets generated successfully.")
