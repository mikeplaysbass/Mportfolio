#!/usr/bin/env python3
"""
sync_calendar.py
Fetches Michael Decena's public Google Calendar feed, parses upcoming tour dates,
and updates assets/tour-dates.json and index.html with:
- Max 8 events per page
- Interactive pagination (if > 8 events)
- "No upcoming performances" empty state (if 0 events)
"""

import os
import re
import json
import math
import urllib.request
from datetime import datetime
import zoneinfo

CALENDAR_ICS_URL = (
    "https://calendar.google.com/calendar/ical/"
    "137a3be20cdf492d3b3cb9f49dd0922692cdfec1d500f95bc8977ff09a2c3672%40group.calendar.google.com"
    "/public/basic.ics"
)

PAGE_SIZE = 8

# Base default European tour shows (Sounds for Someone Tour)
BASE_EUROPE_SHOWS = [
    {
        "isoDate": "2026-11-28T20:00:00+01:00",
        "month": "NOV",
        "day": "28",
        "weekday": "SAT",
        "year": "2026",
        "summary": "Amsterdam Paradiso",
        "city": "Amsterdam",
        "country": "Netherlands",
        "artist": "Elmiene",
        "venue": "Paradiso (Main Hall)",
        "tag": "Sounds for Someone Tour • Extra Date Added",
        "category": "europe",
        "ticketUrl": "#contact",
        "actionLabel": "Tickets",
        "isPrivate": False,
        "source": "base"
    },
    {
        "isoDate": "2026-11-29T20:00:00+01:00",
        "month": "NOV",
        "day": "29",
        "weekday": "SUN",
        "year": "2026",
        "summary": "Amsterdam Melkweg",
        "city": "Amsterdam",
        "country": "Netherlands",
        "artist": "Elmiene",
        "venue": "Melkweg (The Max)",
        "tag": "Sounds for Someone Tour",
        "category": "europe",
        "ticketUrl": "#contact",
        "actionLabel": "Tickets",
        "isPrivate": False,
        "source": "base"
    },
    {
        "isoDate": "2026-11-30T20:00:00+01:00",
        "month": "NOV",
        "day": "30",
        "weekday": "MON",
        "year": "2026",
        "summary": "Berlin Metropol",
        "city": "Berlin",
        "country": "Germany",
        "artist": "Elmiene",
        "venue": "Metropol",
        "tag": "Sounds for Someone Tour",
        "category": "europe",
        "ticketUrl": "#contact",
        "actionLabel": "Tickets",
        "isPrivate": False,
        "source": "base"
    },
    {
        "isoDate": "2026-12-02T20:00:00+01:00",
        "month": "DEC",
        "day": "02",
        "weekday": "WED",
        "year": "2026",
        "summary": "Paris Salle Pleyel",
        "city": "Paris",
        "country": "France",
        "artist": "Elmiene",
        "venue": "Salle Pleyel",
        "tag": "Sounds for Someone Tour • Low Tickets",
        "category": "europe",
        "ticketUrl": "#contact",
        "actionLabel": "Tickets",
        "isPrivate": False,
        "source": "base"
    },
    {
        "isoDate": "2026-12-04T20:00:00+01:00",
        "month": "DEC",
        "day": "04",
        "weekday": "FRI",
        "year": "2026",
        "summary": "Brussels Ancienne Belgique",
        "city": "Brussels",
        "country": "Belgium",
        "artist": "Elmiene",
        "venue": "Ancienne Belgique",
        "tag": "Sounds for Someone Tour",
        "category": "europe",
        "ticketUrl": "#contact",
        "actionLabel": "Tickets",
        "isPrivate": False,
        "source": "base"
    },
    {
        "isoDate": "2026-12-06T20:00:00+00:00",
        "month": "DEC",
        "day": "06",
        "weekday": "SUN",
        "year": "2026",
        "summary": "London Roundhouse",
        "city": "London",
        "country": "United Kingdom",
        "artist": "Elmiene",
        "venue": "Roundhouse (Camden)",
        "tag": "Sounds for Someone UK Tour • Sold Out",
        "category": "europe",
        "ticketUrl": "#contact",
        "actionLabel": "Tickets",
        "isPrivate": False,
        "source": "base"
    },
    {
        "isoDate": "2026-12-08T20:00:00+00:00",
        "month": "DEC",
        "day": "08",
        "weekday": "TUE",
        "year": "2026",
        "summary": "Manchester Albert Hall",
        "city": "Manchester",
        "country": "United Kingdom",
        "artist": "Elmiene",
        "venue": "Albert Hall",
        "tag": "Sounds for Someone UK Tour",
        "category": "europe",
        "ticketUrl": "#contact",
        "actionLabel": "Tickets",
        "isPrivate": False,
        "source": "base"
    },
    {
        "isoDate": "2026-12-10T20:00:00+00:00",
        "month": "DEC",
        "day": "10",
        "weekday": "THU",
        "year": "2026",
        "summary": "London Eventim Apollo",
        "city": "London",
        "country": "United Kingdom",
        "artist": "Elmiene",
        "venue": "Eventim Apollo (Hammersmith)",
        "tag": "Sounds for Someone UK Tour",
        "category": "europe",
        "ticketUrl": "#contact",
        "actionLabel": "Tickets",
        "isPrivate": False,
        "source": "base"
    }
]

def parse_ics_datetime(dt_str, tz_name="America/New_York"):
    dt_str = dt_str.strip()
    if dt_str.endswith("Z"):
        naive = datetime.strptime(dt_str, "%Y%m%dT%H%M%SZ")
        utc_dt = naive.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
        return utc_dt.astimezone(zoneinfo.ZoneInfo(tz_name))
    elif "T" in dt_str:
        naive = datetime.strptime(dt_str, "%Y%m%dT%H%M%S")
        return naive.replace(tzinfo=zoneinfo.ZoneInfo(tz_name))
    else:
        naive = datetime.strptime(dt_str, "%Y%m%d")
        return naive.replace(tzinfo=zoneinfo.ZoneInfo(tz_name))

def parse_description(desc_raw):
    desc = desc_raw.replace("\\n", "\n").replace("\\,", ",").replace("\\;", ";")
    lines = [l.strip() for l in desc.splitlines() if l.strip()]
    
    data = {
        "artist": "",
        "venue": "",
        "tickets": "",
        "tag": ""
    }
    
    for line in lines:
        m = re.match(r"^(artist|performer|band)\s*[-:]\s*(.+)$", line, re.IGNORECASE)
        if m:
            data["artist"] = m.group(2).strip()
            continue
        m = re.match(r"^(venue|place|club)\s*[-:]\s*(.+)$", line, re.IGNORECASE)
        if m:
            data["venue"] = m.group(2).strip()
            continue
        m = re.match(r"^(tickets?|rsvp|link|ticket\s*link)\s*[-:]\s*(https?://\S+)$", line, re.IGNORECASE)
        if m:
            data["tickets"] = m.group(2).strip()
            continue
        m = re.match(r"^(tour|tag|details?|info)\s*[-:]\s*(.+)$", line, re.IGNORECASE)
        if m:
            data["tag"] = m.group(2).strip()
            continue
        url_match = re.search(r"https?://\S+", line)
        if url_match and not data["tickets"]:
            data["tickets"] = url_match.group(0).strip()

    return data

def parse_location(loc_raw):
    loc = loc_raw.replace("\\,", ",").replace("\\n", " ").strip()
    parts = [p.strip() for p in loc.split(",") if p.strip()]
    if len(parts) >= 2:
        return parts[0], ", ".join(parts[1:])
    elif len(parts) == 1:
        return parts[0], "USA" if "new york" in parts[0].lower() else ""
    return "TBA", ""

def fetch_google_calendar_events():
    req = urllib.request.Request(CALENDAR_ICS_URL, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
    
    tz_match = re.search(r"X-WR-TIMEZONE:(.+)", raw)
    tz_name = tz_match.group(1).strip() if tz_match else "America/New_York"
    
    unfolded = re.sub(r"\r?\n[ \t]", "", raw)
    raw_events = re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", unfolded, re.DOTALL)
    
    cal_events = []
    for block in raw_events:
        status_m = re.search(r"STATUS:(.+)", block)
        if status_m and status_m.group(1).strip().upper() == "CANCELLED":
            continue
            
        summary_m = re.search(r"SUMMARY:(.+)", block)
        summary = summary_m.group(1).strip() if summary_m else "Performance"
        
        dtstart_m = re.search(r"DTSTART(?:;[^:]+)?:(.+)", block)
        if not dtstart_m:
            continue
        dt = parse_ics_datetime(dtstart_m.group(1), tz_name)
        
        loc_m = re.search(r"LOCATION:(.+)", block)
        loc_raw = loc_m.group(1).strip() if loc_m else ""
        city, country = parse_location(loc_raw)
        
        desc_m = re.search(r"DESCRIPTION:(.+)", block)
        desc_raw = desc_m.group(1).strip() if desc_m else ""
        desc_data = parse_description(desc_raw)
        
        artist = desc_data["artist"] or summary
        if "private" in summary.lower() and desc_data["artist"]:
            artist = desc_data["artist"]
        
        venue = desc_data["venue"] or ("Private Venue" if "private" in summary.lower() else (city if city != "TBA" else "Live Venue"))
        if venue.lower() == "private":
            venue = "Private Venue"
            
        tag = desc_data["tag"]
        if not tag:
            if "private" in summary.lower() or "private" in venue.lower():
                tag = "Private Performance • Inquire for Bookings"
            else:
                tag = summary if summary != artist else "Live Performance"
                
        full_loc = (loc_raw + " " + summary + " " + desc_raw).lower()
        if any(c in full_loc for c in ["uk", "london", "europe", "amsterdam", "paris", "berlin", "brussels", "germany", "france", "netherlands"]):
            category = "europe"
        elif any(c in full_loc for c in ["new york", "nyc", "los angeles", "la", "chicago", "nashville", "usa", "us"]):
            category = "us"
        else:
            category = "all"
            
        is_private = "private" in summary.lower() or "private" in venue.lower()
        ticket_url = desc_data["tickets"] or "#contact"
        action_label = "Private Event" if is_private else ("Tickets" if desc_data["tickets"] else "Tickets")

        cal_events.append({
            "isoDate": dt.isoformat(),
            "month": dt.strftime("%b").upper(),
            "day": dt.strftime("%d"),
            "weekday": dt.strftime("%a").upper(),
            "year": dt.strftime("%Y"),
            "summary": summary,
            "city": city,
            "country": country,
            "artist": artist,
            "venue": venue,
            "tag": tag,
            "category": category,
            "ticketUrl": ticket_url,
            "actionLabel": action_label,
            "isPrivate": is_private,
            "source": "calendar"
        })
        
    return cal_events

def generate_tour_cards_html(events):
    empty_style = "display: flex;" if len(events) == 0 else "display: none;"
    
    empty_html = f"""          <!-- Empty State (Displayed when 0 shows are scheduled) -->
          <div id="tour-empty-state" class="tour-empty-state" role="status" aria-live="polite" style="{empty_style}">
            <div class="tour-empty-icon" aria-hidden="true">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
            </div>
            <h3 class="tour-empty-title">No Upcoming Performances Scheduled</h3>
            <p class="tour-empty-subtitle">New headline dates, festival appearances, and live shows are currently in preparation. Check back soon or submit an inquiry below for booking commissions and sessions.</p>
            <a href="#contact" class="btn btn-primary tour-empty-btn">
              Book Michael Decena
            </a>
          </div>"""

    if not events:
        return empty_html

    cards_html = [empty_html]
    for i, ev in enumerate(events, 1):
        target_attr = ' target="_blank" rel="noopener noreferrer"' if ev["ticketUrl"].startswith("http") else ''
        aria_label = f"Inquire about {ev['month']} {ev['day']} {ev['summary']} in {ev['city']}" if ev['isPrivate'] else f"Get tickets for {ev['month']} {ev['day']} at {ev['venue']} {ev['city']}"
        
        # Paginate: Only show the first PAGE_SIZE (8) cards statically
        hide_style = ' style="display: none;"' if (i > PAGE_SIZE) else ''
        
        card = f"""          <!-- Show {i}: {ev['city']} {ev['venue']} -->
          <article class="tour-card" data-category="{ev['category']}" data-tour-index="{i - 1}"{hide_style}>
            <div class="tour-date-col">
              <span class="tour-month">{ev['month']}</span>
              <span class="tour-day">{ev['day']}</span>
              <span class="tour-weekday">{ev['weekday']}</span>
            </div>
            
            <div class="tour-location-col">
              <span class="tour-city">{ev['city']}</span>
              <span class="tour-country">{ev['country']}</span>
            </div>

            <div class="tour-venue-col">
              <span class="tour-artist-name">{ev['artist']}</span>
              <span class="tour-venue">{ev['venue']}</span>
              <span class="tour-details-tag">
                {ev['tag']}
              </span>
            </div>

            <div class="tour-action-col">
              <a href="{ev['ticketUrl']}" class="btn btn-primary"{target_attr} aria-label="{aria_label}">
                {ev['actionLabel']}
              </a>
            </div>
          </article>"""
        cards_html.append(card)
        
    return "\n\n".join(cards_html)

def generate_pagination_html(total_events):
    total_pages = math.ceil(total_events / PAGE_SIZE) if total_events > 0 else 1
    nav_style = "display: flex;" if total_pages > 1 else "display: none;"
    
    page_nums_html = []
    for p in range(1, total_pages + 1):
        active_cls = " active" if p == 1 else ""
        current_attr = ' aria-current="page"' if p == 1 else ""
        btn = f'<button class="tour-page-num{active_cls}" type="button" aria-label="Page {p}"{current_attr}>{p}</button>'
        page_nums_html.append(f"            {btn}")
        
    pages_inner = "\n".join(page_nums_html) if page_nums_html else ""
    
    return f"""        <!-- Tour Pagination Controls (Max {PAGE_SIZE} Shows per Page) -->
        <nav id="tour-pagination" class="tour-pagination" aria-label="Tour dates pagination" style="{nav_style}">
          <button id="tour-page-prev" class="tour-page-btn tour-page-prev" type="button" aria-label="Previous page of tour dates" disabled>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
            <span>Prev</span>
          </button>
          
          <div id="tour-page-numbers" class="tour-page-numbers" role="navigation" aria-label="Page numbers">
{pages_inner}
          </div>

          <button id="tour-page-next" class="tour-page-btn tour-page-next" type="button" aria-label="Next page of tour dates">
            <span>Next</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>
        </nav>"""

def main():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(repo_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    json_path = os.path.join(assets_dir, "tour-dates.json")
    index_path = os.path.join(repo_dir, "index.html")

    print("[1/4] Fetching Google Calendar feed...")
    try:
        cal_events = fetch_google_calendar_events()
        print(f"      Successfully fetched {len(cal_events)} event(s) from Google Calendar.")
    except Exception as e:
        print(f"      [WARN] Failed to fetch Google Calendar feed: {e}")
        cal_events = []

    # Merge calendar events with base European shows (calendar takes precedence if same city/date)
    all_events = list(cal_events)
    cal_keys = {(e["city"].lower(), e["month"], e["day"]) for e in cal_events}
    
    for base_ev in BASE_EUROPE_SHOWS:
        key = (base_ev["city"].lower(), base_ev["month"], base_ev["day"])
        if key not in cal_keys:
            all_events.append(base_ev)
            
    # Sort chronologically
    all_events.sort(key=lambda e: e["isoDate"])
    print(f"[2/4] Total tour events: {len(all_events)} (Paginated at max {PAGE_SIZE} per page)")

    # Write assets/tour-dates.json
    print(f"[3/4] Writing {json_path}...")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_events, f, indent=2, ensure_ascii=False)
    print("      JSON written successfully.")

    # Update index.html
    print(f"[4/4] Updating {index_path}...")
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    cards_html = generate_tour_cards_html(all_events)
    pagination_html = generate_pagination_html(len(all_events))
    
    start_marker = "<!-- TOUR_DATES_START -->"
    end_marker = "<!-- TOUR_DATES_END -->"

    if start_marker in content and end_marker in content:
        pattern = re.compile(rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
        replacement = f"{start_marker}\n{cards_html}\n          {end_marker}"
        content = pattern.sub(replacement, content)
    else:
        # First time insertion
        list_match = re.search(r'(<div class="tour-list"[^>]*>)(.*?)(</div>\s*</div>\s*</section>)', content, re.DOTALL)
        if list_match:
            open_tag = list_match.group(1)
            close_tags = list_match.group(3)
            new_block = f"{open_tag}\n          {start_marker}\n{cards_html}\n          {end_marker}\n        {close_tags}"
            content = content[:list_match.start()] + new_block + content[list_match.end():]

    # Ensure Pagination block is present right after </div> of .tour-list
    pag_start = "<!-- TOUR_PAGINATION_START -->"
    pag_end = "<!-- TOUR_PAGINATION_END -->"
    pag_block = f"{pag_start}\n{pagination_html}\n        {pag_end}"

    if pag_start in content and pag_end in content:
        pag_pattern = re.compile(rf"{re.escape(pag_start)}.*?{re.escape(pag_end)}", re.DOTALL)
        content = pag_pattern.sub(pag_block, content)
    else:
        # Insert after </div> of tour-list
        tour_list_close = '</div>\n\n      </div>\n    </section>'
        if tour_list_close in content:
            replacement = f'</div>\n\n        {pag_block}\n\n      </div>\n    </section>'
            content = content.replace(tour_list_close, replacement, 1)
        else:
            # Fallback regex search
            m = re.search(r'(<!-- TOUR_DATES_END -->\s*</div>)', content)
            if m:
                content = content[:m.end()] + f"\n\n        {pag_block}" + content[m.end():]

    # Ensure North America filter button is present
    if 'data-filter="us"' not in content:
        filter_target = '<button class="filter-pill active" role="tab" aria-selected="true" data-filter="all">All Dates</button>'
        filter_replacement = (
            '<button class="filter-pill active" role="tab" aria-selected="true" data-filter="all">All Dates</button>\n'
            '          <button class="filter-pill" role="tab" aria-selected="false" data-filter="us">North America</button>'
        )
        content = content.replace(filter_target, filter_replacement)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("      index.html updated successfully with pagination & empty state support!")

if __name__ == "__main__":
    main()
