#!/usr/bin/env python3
"""
sync_calendar.py
Fetches Michael Decena's public Google Calendar feed, parses upcoming tour dates,
and updates assets/tour-dates.json and index.html according to strict user specifications:

Format in Description:
City: New York City
Country: USA
Artist: 
Venue: 
Tour Name
Tickets: Y
Link: https://link-to-tickets.com
Optional link: https://elementmusic.com
Venue Location: [Specific address / neighborhood / area] (rendered below country)
Region: North America

If region is populated, create a tab for it; otherwise if it's already there, group it with the others.
If any are left blank, just leave their section empty.
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

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")

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
        # All-day event YYYYMMDD
        naive = datetime.strptime(dt_str, "%Y%m%d")
        return naive.replace(tzinfo=zoneinfo.ZoneInfo(tz_name))

def parse_description(desc_raw):
    """
    Parses structured description lines according to user format:
    Country: <country>
    Artist: <artist>
    Venue: <venue>
    Tour Name: <tour_name>
    Tickets: Y/N
    Link: <tickets_url>
    Optional link: <artist_url>
    Venue Location: <venue_location>
    Region: <region>
    
    If any are left blank, just leave their section empty.
    """
    desc = desc_raw.replace("\\n", "\n").replace("\\,", ",").replace("\\;", ";")
    lines = [l.strip() for l in desc.splitlines() if l.strip()]
    
    data = {
        "city": "",
        "city_set": False,
        "country": "",
        "country_set": False,
        "artist": "",
        "venue": "",
        "tour_name": "",
        "tickets_flag": None,  # True if Y, False if N, None if not set
        "link": "",
        "optional_link": "",
        "venue_location": "",
        "region": "",
    }
    
    for line in lines:
        # 0. City (parsed directly from description)
        m = re.match(r"^city\s*[-:]\s*(.*)$", line, re.IGNORECASE)
        if m:
            data["city_set"] = True
            data["city"] = m.group(1).strip()
            continue

        # 1. Country
        m = re.match(r"^country\s*[-:]\s*(.*)$", line, re.IGNORECASE)
        if m:
            data["country_set"] = True
            data["country"] = m.group(1).strip()
            continue
            
        # 2. Artist
        m = re.match(r"^artist\s*[-:]\s*(.*)$", line, re.IGNORECASE)
        if m:
            data["artist"] = m.group(1).strip()
            continue
            
        # 3. Venue Location (Check before Venue to avoid prefix collision!)
        m = re.match(r"^(?:venue\s*location|venue\s*address)\s*[-:]\s*(.*)$", line, re.IGNORECASE)
        if m:
            data["venue_location"] = m.group(1).strip()
            continue
            
        # 4. Venue
        m = re.match(r"^venue\s*[-:]\s*(.*)$", line, re.IGNORECASE)
        if m:
            data["venue"] = m.group(1).strip()
            continue
            
        # 5. Tour Name
        m = re.match(r"^(?:tour\s*name|tour)(?:\s*[-:]\s*(.*))?$", line, re.IGNORECASE)
        if m:
            captured = m.group(1)
            data["tour_name"] = captured.strip() if captured else ""
            continue
            
        # 6. Tickets flag (Y / N or y / n)
        m = re.match(r"^tickets?\s*[-:]\s*(.*)$", line, re.IGNORECASE)
        if m:
            val = m.group(1).strip().upper()
            if val in ["Y", "YES", "TRUE"]:
                data["tickets_flag"] = True
            elif val in ["N", "NO", "FALSE"]:
                data["tickets_flag"] = False
            else:
                data["tickets_flag"] = None
            continue
            
        # 7. Optional link (for hyperlinking artist name - check before Link!)
        m = re.match(r"^(?:optional\s*link|artist\s*link|website|site)\s*[-:]\s*(https?://\S+)", line, re.IGNORECASE)
        if m:
            data["optional_link"] = m.group(1).strip()
            continue
            
        # 8. Link (for ticket button)
        m = re.match(r"^(?:ticket\s*link|link)\s*[-:]\s*(https?://\S+)", line, re.IGNORECASE)
        if m:
            data["link"] = m.group(1).strip()
            continue

        # 9. Region
        m = re.match(r"^region\s*[-:]\s*(.*)$", line, re.IGNORECASE)
        if m:
            data["region"] = m.group(1).strip()
            continue

        # Fallback raw URL: if line is just a URL and no ticket link yet
        if line.startswith("http://") or line.startswith("https://"):
            if not data["link"]:
                data["link"] = line.strip()

    return data

def resolve_city_and_country(summary_raw, loc_raw, desc_data):
    """
    User rule:
    Rather than taking city from title, take it from Description:
      City: <city>
      Country: <country>
    If any are left blank just leave their section empty.
    Fallback to Event Title / Location if City/Country are not specified in Description.
    """
    summary = summary_raw.replace("\\,", ",").replace("\\n", " ").strip()
    loc = loc_raw.replace("\\,", ",").replace("\\n", " ").strip()
    
    # 1. City resolution (prefer explicit City: from description)
    if desc_data.get("city_set"):
        city = desc_data.get("city", "").strip()
    else:
        # Fallback for legacy events without City: in description
        is_placeholder = summary.lower().startswith("private") or summary.lower() in ["performance", "show", "tour date"]
        target_text = loc if (is_placeholder and loc) else summary
        if "," in target_text:
            city = target_text.split(",")[0].strip()
        else:
            city = target_text

    # 2. Country resolution (prefer explicit Country: from description)
    if desc_data.get("country_set"):
        country = desc_data.get("country", "").strip()
    else:
        # Fallback for legacy events without Country: in description
        is_placeholder = summary.lower().startswith("private") or summary.lower() in ["performance", "show", "tour date"]
        target_text = loc if (is_placeholder and loc) else summary
        if "," in target_text:
            parts = [p.strip() for p in target_text.split(",") if p.strip()]
            country = ", ".join(parts[1:]) if len(parts) > 1 else ""
        else:
            country = ""
            
    return city, country

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
        summary_raw = summary_m.group(1).strip() if summary_m else ""
        
        dtstart_m = re.search(r"DTSTART(?:;[^:]+)?:(.+)", block)
        if not dtstart_m:
            continue
        dt = parse_ics_datetime(dtstart_m.group(1), tz_name)
        
        loc_m = re.search(r"LOCATION:(.+)", block)
        loc_raw = loc_m.group(1).strip() if loc_m else ""
        
        desc_m = re.search(r"DESCRIPTION:(.+)", block)
        desc_raw = desc_m.group(1).strip() if desc_m else ""
        desc_data = parse_description(desc_raw)
        
        city, country = resolve_city_and_country(summary_raw, loc_raw, desc_data)
        
        # Artist: if left blank, leave empty
        artist = desc_data["artist"]
        
        # Venue: if left blank, leave empty
        venue = desc_data["venue"]
        
        # Venue Location: if left blank, leave empty
        venue_location = desc_data["venue_location"]
        
        # Tour Name: if left blank, leave empty
        tour_name = desc_data["tour_name"]
        
        # Region & category slug:
        # If region is populated create a tab for it, otherwise if already there group it with others
        # If left blank, leaves category as "all"
        region = desc_data["region"]
        category_slug = slugify(region) if region else "all"
        
        # Is private?
        is_private = (
            summary_raw.lower().startswith("private") or
            artist.lower() == "private" or
            venue.lower() == "private" or
            desc_data["tickets_flag"] is False
        )
        
        # Ticket button rule:
        # "if the event is labeled as a private event there should not be a button otherwise the only button there should say tickets"
        # "Tickets/tickets: Y/N or y/n (this is for the buttons, could use a flag)"
        # "If any are left blank just leave their section empty"
        if is_private or desc_data["tickets_flag"] is not True:
            has_tickets = False
        else:
            has_tickets = True

        ticket_url = desc_data["link"] or "#contact"

        cal_events.append({
            "isoDate": dt.isoformat(),
            "month": dt.strftime("%b").upper(),
            "day": dt.strftime("%d"),
            "weekday": dt.strftime("%a").upper(),
            "year": dt.strftime("%Y"),
            "summary": summary_raw,
            "city": city,
            "country": country,
            "venueLocation": venue_location,
            "artist": artist,
            "optionalLink": desc_data["optional_link"],
            "venue": venue,
            "tourName": tour_name,
            "region": region,
            "category": category_slug,
            "hasTickets": has_tickets,
            "ticketUrl": ticket_url,
            "source": "calendar"
        })
        
    return cal_events

def generate_filter_bar_html(events):
    """
    Builds the category filter pills:
    - Always starts with 'All Dates'
    - Dynamically generates tabs for each unique populated Region (e.g. 'North America', 'Europe')
    - If multiple events share a region, they are grouped under that single tab
    - If no regions are populated, only 'All Dates' is displayed
    """
    seen_slugs = set()
    regions = []
    for ev in events:
        reg = ev.get("region", "").strip()
        if reg:
            slug = slugify(reg)
            if slug and slug not in seen_slugs and slug != "all":
                seen_slugs.add(slug)
                regions.append((slug, reg))
                
    buttons = [
        '<button class="filter-pill active" role="tab" aria-selected="true" data-filter="all">All Dates</button>'
    ]
    for slug, label in regions:
        escaped_label = label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        buttons.append(
            f'<button class="filter-pill" role="tab" aria-selected="false" data-filter="{slug}">{escaped_label}</button>'
        )
        
    pills_html = "\n            ".join(buttons)
    return f"""          <!-- Category Filter Pills (ARIA Tablist pattern) -->
          <div class="tour-filter-bar" role="tablist" aria-label="Tour category filter" style="display: flex !important; align-items: center !important; gap: 0.75rem !important; flex: 1 1 auto !important; min-width: 0 !important; overflow-x: auto !important; overflow-y: hidden !important; white-space: nowrap !important; flex-wrap: nowrap !important; margin: 0 !important;">
            {pills_html}
          </div>"""

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
        # 1. Location Column elements:
        # City (Event Title)
        city_html = f'<span class="tour-city">{ev["city"]}</span>' if ev.get("city") else ''
        # Country (from Country:)
        country_html = f'\n              <span class="tour-country">{ev["country"]}</span>' if ev.get("country") else ''
        # Venue Location (added below country!)
        venue_loc_html = f'\n              <span class="tour-venue-location">{ev["venueLocation"]}</span>' if ev.get("venueLocation") else ''
        
        location_inner = f"{city_html}{country_html}{venue_loc_html}".strip()
        location_col_html = f"""\n            <div class="tour-location-col">
              {location_inner}
            </div>""" if location_inner else '\n            <div class="tour-location-col"></div>'

        # 2. Venue Column elements:
        # Artist: hyperlinked if optionalLink provided, else plain text
        if ev.get("artist"):
            if ev.get("optionalLink"):
                artist_content = f'<a href="{ev["optionalLink"]}" target="_blank" rel="noopener noreferrer" class="tour-artist-link">{ev["artist"]}</a>'
            else:
                artist_content = ev["artist"]
            artist_html = f'\n              <span class="tour-artist-name">{artist_content}</span>'
        else:
            artist_html = ''

        # Venue element
        venue_html = f'\n              <span class="tour-venue">{ev["venue"]}</span>' if ev.get("venue") else ''

        # Tour Name element
        tour_name_html = f'\n              <span class="tour-details-tag">\n                {ev["tourName"]}\n              </span>' if ev.get("tourName") else ''

        venue_inner = f"{artist_html}{venue_html}{tour_name_html}".strip()
        venue_col_html = f"""\n            <div class="tour-venue-col">
              {venue_inner}
            </div>""" if venue_inner else '\n            <div class="tour-venue-col"></div>'

        # 3. Action Column element: ticket button ONLY if hasTickets is True. No button for private / unticketed!
        if ev.get("hasTickets"):
            target_attr = ' target="_blank" rel="noopener noreferrer"' if ev.get("ticketUrl", "").startswith("http") else ''
            aria_label = f"Get tickets for {ev['month']} {ev['day']} in {ev['city']}"
            ticket_url = ev.get("ticketUrl") or "#contact"
            action_html = f"""\n            <div class="tour-action-col">
              <a href="{ticket_url}" class="btn btn-primary"{target_attr} aria-label="{aria_label}">
                Tickets
              </a>
            </div>"""
        else:
            action_html = """\n            <div class="tour-action-col">
              <!-- Private / un-ticketed event: no button -->
            </div>"""

        # Paginate: Only show the first PAGE_SIZE (8) cards statically
        hide_style = ' style="display: none;"' if (i > PAGE_SIZE) else ''
        
        region_attr = f' data-region="{ev["region"]}"' if ev.get("region") else ''
        
        card = f"""          <!-- Show {i}: {ev['city']} -->
          <article class="tour-card" data-category="{ev['category']}"{region_attr} data-date="{ev['isoDate']}" data-tour-index="{i - 1}"{hide_style}>
            <div class="tour-date-col">
              <span class="tour-month">{ev['month']}</span>
              <span class="tour-day">{ev['day']}</span>
              <span class="tour-weekday">{ev['weekday']}</span>
            </div>{location_col_html}
{venue_col_html}{action_html}
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

    # USER RULE: Only pick up dates from Google Calendar (no hardcoded shows)
    all_events = list(cal_events)
            
    # USER RULE: Tour dates sorted by date (default ascending)
    all_events.sort(key=lambda e: e["isoDate"])
    print(f"[2/4] Total live Google Calendar events: {len(all_events)} (Sorted by date)")

    # Write assets/tour-dates.json
    print(f"[3/4] Writing {json_path}...")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_events, f, indent=2, ensure_ascii=False)
    print("      JSON written successfully.")

    # Update index.html
    print(f"[4/4] Updating {index_path}...")
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update filter pills bar based on populated regions
    filters_html = generate_filter_bar_html(all_events)
    filter_start = "<!-- TOUR_FILTERS_START -->"
    filter_end = "<!-- TOUR_FILTERS_END -->"

    if filter_start in content and filter_end in content:
        filter_pattern = re.compile(rf"{re.escape(filter_start)}.*?{re.escape(filter_end)}", re.DOTALL)
        content = filter_pattern.sub(f"{filter_start}\n{filters_html}\n          {filter_end}", content)
    else:
        m = re.search(r'(<div class="tour-filter-bar"[^>]*>.*?</div>)', content, re.DOTALL)
        if m:
            content = content[:m.start()] + f"{filter_start}\n{filters_html}\n          {filter_end}" + content[m.end():]

    # 2. Update tour cards
    cards_html = generate_tour_cards_html(all_events)
    start_marker = "<!-- TOUR_DATES_START -->"
    end_marker = "<!-- TOUR_DATES_END -->"

    if start_marker in content and end_marker in content:
        pattern = re.compile(rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
        content = pattern.sub(f"{start_marker}\n{cards_html}\n          {end_marker}", content)
    else:
        list_match = re.search(r'(<div class="tour-list"[^>]*>)(.*?)(</div>\s*</div>\s*</section>)', content, re.DOTALL)
        if list_match:
            open_tag = list_match.group(1)
            close_tags = list_match.group(3)
            new_block = f"{open_tag}\n          {start_marker}\n{cards_html}\n          {end_marker}\n        {close_tags}"
            content = content[:list_match.start()] + new_block + content[list_match.end():]

    # 3. Update pagination
    pagination_html = generate_pagination_html(len(all_events))
    pag_start = "<!-- TOUR_PAGINATION_START -->"
    pag_end = "<!-- TOUR_PAGINATION_END -->"
    pag_block = f"{pag_start}\n{pagination_html}\n        {pag_end}"

    if pag_start in content and pag_end in content:
        pag_pattern = re.compile(rf"{re.escape(pag_start)}.*?{re.escape(pag_end)}", re.DOTALL)
        content = pag_pattern.sub(pag_block, content)
    else:
        m = re.search(r'(<!-- TOUR_DATES_END -->\s*</div>)', content)
        if m:
            content = content[:m.end()] + f"\n\n        {pag_block}" + content[m.end():]

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("      index.html updated successfully with dynamic region tabs & new scrape format!")

if __name__ == "__main__":
    main()
