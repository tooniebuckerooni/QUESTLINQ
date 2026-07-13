#!/usr/bin/env python3
"""QuestLinq static site generator. Stdlib only.

Reads data/*.json + templates/*.html, writes the finished site to public/.
Run from the repo root:  python3 build.py
"""
import json
import shutil
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).parent
DATA = ROOT / "data"
TPL = ROOT / "templates"
OUT = ROOT / "public"
TZ = ZoneInfo("America/Toronto")

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DAY_NAMES = {"mon": "Monday", "tue": "Tuesday", "wed": "Wednesday", "thu": "Thursday",
             "fri": "Friday", "sat": "Saturday", "sun": "Sunday"}

site = json.loads((DATA / "site.json").read_text())
hosts = json.loads((DATA / "hosts.json").read_text())
events = json.loads((DATA / "events.json").read_text())
packs = json.loads((DATA / "packs.json").read_text())
CATS = site["categories"]
DOMAIN = site["domain"]
CITY = site["cities"][0]
BASE = (TPL / "base.html").read_text()

hosts_by_slug = {h["slug"]: h for h in hosts}
packs_by_slug = {p["slug"]: p for p in packs}


def next_occurrence(weekday: str, start_time: str) -> datetime:
    """Next date (today included) falling on `weekday`, at start_time, in Toronto time."""
    today = datetime.now(TZ).date()
    target = DAYS.index(weekday)
    delta = (target - today.weekday()) % 7
    d = today + timedelta(days=delta)
    h, m = map(int, start_time.split(":"))
    return datetime(d.year, d.month, d.day, h, m, tzinfo=TZ)


def jsonld(obj) -> str:
    return '<script type="application/ld+json">%s</script>' % json.dumps(obj, ensure_ascii=False)


def breadcrumbs(*items):
    return {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": DOMAIN + path}
            for i, (name, path) in enumerate(items)
        ],
    }


ORG_LD = {
    "@context": "https://schema.org", "@type": "Organization",
    "name": "QuestLinq", "url": DOMAIN, "logo": DOMAIN + "/assets/img/gold-shield-primary.png",
    "email": site["contact_email"], "slogan": site["tagline"],
}


def page(path: str, *, title, description, content, ld=None, nav=None, body_attrs="",
         og_image="/assets/img/gold-shield-primary.png"):
    """Render a page into public/<path>/index.html (or public/<path> if it ends in .html)."""
    canonical = DOMAIN + path
    navs = {k: "" for k in ("nav_events", "nav_hosts", "nav_packs", "nav_venues", "nav_host")}
    if nav:
        navs[nav] = 'aria-current="page"'
    blocks = [jsonld(ORG_LD)] + [jsonld(x) for x in (ld or [])]
    html = BASE
    for k, v in {
        "title": escape(title), "description": escape(description), "canonical": canonical,
        "og_image": DOMAIN + og_image, "jsonld": "\n".join(blocks), "content": content,
        "year": str(datetime.now(TZ).year), "body_attrs": body_attrs, **navs,
    }.items():
        html = html.replace("{{%s}}" % k, v)
    dest = OUT / path.lstrip("/")
    if not path.endswith(".html"):
        dest = dest / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html)
    if not path.endswith(".html"):
        SITEMAP.append(path)


def tpl(name: str, **tokens) -> str:
    t = (TPL / name).read_text()
    for k, v in tokens.items():
        t = t.replace("{{%s}}" % k, v)
    return t


def sample_badge(item) -> str:
    return ' <span class="badge badge-sample">Example listing</span>' if item.get("sample") else ""


def sample_notice(item) -> str:
    if not item.get("sample"):
        return ""
    return ('<p class="sample-notice"><strong>Example listing.</strong> This is sample content '
            "showing what a live QuestLinq listing looks like — real Kingston listings are on the way. "
            'Run events here? <a href="/become-a-host/">List yourself free</a>.</p>')


# ---------------------------------------------------------------- cards

def event_card(ev) -> str:
    host = hosts_by_slug[ev["host_slug"]]
    price = ('<span class="badge badge-free">Free</span>' if ev["price"]["type"] == "free"
             else '<span class="price-tag">$%d</span>' % ev["price"]["cad"])
    when = "Every %s · %s" % (DAY_NAMES[ev["weekday"]], fmt_time(ev["start_time"]))
    return f'''      <article class="card" data-weekday="{ev["weekday"]}">
        <div class="card-meta"><span>{escape(CATS[ev["category"]])}</span> {price}{sample_badge(ev)}</div>
        <h3><a href="/events/{ev["slug"]}/">{escape(ev["title"])}</a></h3>
        <p>{escape(when)} · {escape(ev["venue"]["name"])}</p>
        <p>Hosted by {escape(host["name"])}</p>
        <p class="card-cta"><a class="btn btn-ghost btn-sm" href="/events/{ev["slug"]}/">Details →</a></p>
      </article>'''


def host_card(h) -> str:
    types = " · ".join(CATS[t] for t in h["event_types"])
    verified = ' <span class="badge badge-gold">Verified</span>' if h.get("verified") else ""
    return f'''      <article class="card">
        <div class="card-meta"><span>{escape(types)}</span>{verified}{sample_badge(h)}</div>
        <h3><a href="/hosts/{h["slug"]}/">{escape(h["name"])}</a></h3>
        <p>{escape(h["tagline"])}</p>
        <p>Draws {escape(h["typical_draw"])} · From ${h["pricing_guidance"]["from_cad"]}/event</p>
        <p class="card-cta"><a class="btn btn-ghost btn-sm" href="/hosts/{h["slug"]}/">View profile →</a></p>
      </article>'''


def pack_card(p) -> str:
    badge = f' <span class="badge badge-teal">{escape(p["badge"])}</span>' if p.get("badge") else ""
    return f'''      <article class="card">
        <div class="card-meta"><span class="price-tag">CA${p["price_cad"]}</span>{badge}</div>
        <h3><a href="/packs/{p["slug"]}/">{escape(p["short_title"])}</a></h3>
        <p>{escape(p["tagline"])}</p>
        <p class="card-cta"><a class="btn btn-gold btn-sm" href="/packs/{p["slug"]}/">Get the kit →</a></p>
      </article>'''


def fmt_time(t: str) -> str:
    h, m = map(int, t.split(":"))
    suffix = "PM" if h >= 12 else "AM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {suffix}" if m else f"{h12} {suffix}"


def event_ld(ev):
    host = hosts_by_slug[ev["host_slug"]]
    start = next_occurrence(ev["weekday"], ev["start_time"])
    end = start + timedelta(hours=ev["duration_hours"])
    offers = {"@type": "Offer", "url": DOMAIN + f'/events/{ev["slug"]}/',
              "priceCurrency": "CAD",
              "price": 0 if ev["price"]["type"] == "free" else ev["price"]["cad"],
              "availability": "https://schema.org/InStock"}
    return {
        "@context": "https://schema.org", "@type": "Event",
        "name": ev["title"], "description": ev["description"],
        "startDate": start.isoformat(), "endDate": end.isoformat(),
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "eventStatus": "https://schema.org/EventScheduled",
        "location": {"@type": "Place", "name": ev["venue"]["name"],
                     "address": ev["venue"]["address"]},
        "performer": {"@type": "PerformingGroup", "name": host["name"]},
        "organizer": {"@type": "Organization", "name": "QuestLinq", "url": DOMAIN},
        "offers": offers, "image": DOMAIN + "/assets/img/gold-shield-primary.png",
    }


# ---------------------------------------------------------------- pages

SITEMAP: list[str] = []


def build_assets():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets/img").mkdir(parents=True)
    shutil.copytree(ROOT / "assets/css", OUT / "assets/css")
    shutil.copytree(ROOT / "assets/js", OUT / "assets/js")
    for f in ["questlinq-mark.svg", "questlinq-wordmark.svg"]:
        shutil.copy(ROOT / "brand" / f, OUT / "assets/img" / f)
    shutil.copy(ROOT / "brand/favicon.svg", OUT / "favicon.svg")
    for f in ["gold-shield-primary.png", "chrome-shield-secondary.png", "about-us-collage.png"]:
        shutil.copy(ROOT / "brand/logos" / f, OUT / "assets/img" / f)


def build_home():
    preview = "\n".join(event_card(e) for e in events[:6])
    top = [packs_by_slug[s] for s in
           ["murder-mystery-night", "fantasy-tavern-party", "complete-mystery-collection"]]
    strip = "\n".join(pack_card(p) for p in top)
    page("/", title="QuestLinq — Events in Kingston, Ontario | Events That Bring Us Together",
         description="Find free and ticketed event nights in Kingston tonight — trivia, murder mystery, "
                     "comedy, karaoke. Venues: find and book event hosts. Hosts: get booked, never pay for leads.",
         content=tpl("index.html", events_preview=preview, packs_strip=strip),
         ld=[{"@context": "https://schema.org", "@type": "WebSite", "name": "QuestLinq",
              "url": DOMAIN}])


def events_hub_content(evs, heading, sub, active, note=False):
    chips = ['<a class="chip%s" href="/events/on/kingston/">All</a>' % (" active" if active == "all" else "")]
    chips += ['<a class="chip%s" href="/events/on/kingston/tonight/">Tonight</a>' % (" active" if active == "tonight" else ""),
              '<a class="chip%s" href="/events/on/kingston/this-weekend/">This weekend</a>' % (" active" if active == "weekend" else ""),
              '<a class="chip%s" href="/events/on/kingston/free/">Free</a>' % (" active" if active == "free" else "")]
    for c, label in CATS.items():
        if any(e["category"] == c for e in events):
            chips.append('<a class="chip%s" href="/events/on/kingston/%s/">%s</a>'
                         % (" active" if active == c else "", c, escape(label)))
    cards = "\n".join(event_card(e) for e in evs)
    note_html = '<p class="section-sub" data-filter-note></p>' if note else ""
    return f'''<section class="page-hero"><div class="container">
  <p class="eyebrow">Kingston, Ontario</p>
  <h1>{heading}</h1>
  <p class="hero-sub">{sub}</p>
</div></section>
<section class="section"><div class="container">
  <div class="filter-row">{''.join(chips)}</div>
  {note_html}
  <div class="card-grid">
{cards}
  </div>
  <p class="section-more footnote">Run events in Kingston? <a href="/become-a-host/">List yourself free</a> —
  venues pay to reach you. Own a venue? <a href="/for-venues/">Find your host</a>.</p>
</div></section>'''


def build_events():
    city_path = f'/events/{CITY["province"]}/{CITY["slug"]}/'
    ld_list = {
        "@context": "https://schema.org", "@type": "ItemList",
        "itemListElement": [{"@type": "ListItem", "position": i + 1,
                             "url": DOMAIN + f'/events/{e["slug"]}/'} for i, e in enumerate(events)],
    }
    page(city_path, nav="nav_events",
         title=f'Events in Kingston, Ontario — tonight & this week | QuestLinq',
         description="Everything happening in Kingston: trivia nights, murder mysteries, comedy, "
                     "karaoke, and quest nights at local pubs and breweries. Free and ticketed.",
         content=events_hub_content(events, "What's on in Kingston", CITY["region_blurb"], "all"),
         ld=[ld_list, breadcrumbs(("Home", "/"), ("Events", city_path))])

    page(city_path + "tonight/", nav="nav_events", body_attrs=' data-date-filter="tonight"',
         title="Things to do in Kingston tonight | QuestLinq",
         description="What's on in Kingston tonight: trivia, mystery nights, comedy, karaoke and more "
                     "at local pubs and breweries.",
         content=events_hub_content(events, "Things to do in Kingston <em>tonight</em>",
                                    "Live event nights happening today.", "tonight", note=True),
         ld=[breadcrumbs(("Home", "/"), ("Events", city_path), ("Tonight", city_path + "tonight/"))])

    page(city_path + "this-weekend/", nav="nav_events", body_attrs=' data-date-filter="weekend"',
         title="Kingston events this weekend | QuestLinq",
         description="Friday to Sunday in Kingston: event nights at pubs, breweries and cafés — "
                     "fantasy taverns, karaoke, puzzle quests and more.",
         content=events_hub_content(events, "Kingston events <em>this weekend</em>",
                                    "Friday through Sunday.", "weekend", note=True),
         ld=[breadcrumbs(("Home", "/"), ("Events", city_path), ("This weekend", city_path + "this-weekend/"))])

    free = [e for e in events if e["price"]["type"] == "free"]
    if free:
        page(city_path + "free/", nav="nav_events",
             title="Free events in Kingston this week | QuestLinq",
             description="Free things to do in Kingston: no-cover trivia, music bingo, karaoke, "
                         "open mics and puzzle afternoons.",
             content=events_hub_content(free, "Free events in Kingston",
                                        "No cover, no ticket — just show up.", "free"),
             ld=[breadcrumbs(("Home", "/"), ("Events", city_path), ("Free", city_path + "free/"))])

    for cat, label in CATS.items():
        evs = [e for e in events if e["category"] == cat]
        if not evs:
            continue
        page(city_path + cat + "/", nav="nav_events",
             title=f"{label} nights in Kingston | QuestLinq",
             description=f"{label} events in Kingston, Ontario — dates, venues, and tickets.",
             content=events_hub_content(evs, f"{escape(label)} in Kingston",
                                        f"Every {label.lower()} night we know about.", cat),
             ld=[breadcrumbs(("Home", "/"), ("Events", city_path), (label, city_path + cat + "/"))])

    for ev in events:
        build_event_detail(ev)


def build_event_detail(ev):
    host = hosts_by_slug[ev["host_slug"]]
    nxt = next_occurrence(ev["weekday"], ev["start_time"])
    price_row = ("<li><strong>Price:</strong> Free — just show up</li>" if ev["price"]["type"] == "free"
                 else f'<li><strong>Tickets:</strong> ${ev["price"]["cad"]} CAD</li>')
    cta = ('<a class="btn btn-gold" href="mailto:hello@questlinq.com?subject=RSVP%%20—%%20%s">RSVP free by email</a>'
           % escape(ev["title"]) if ev["price"]["type"] == "free" else
           '<a class="btn btn-gold" href="mailto:hello@questlinq.com?subject=Tickets%%20—%%20%s">Get tickets</a>'
           % escape(ev["title"]))
    pack_link = ""
    related = {"murder-mystery": "murder-mystery-night", "fantasy-tavern": "fantasy-tavern-party",
               "puzzle-escape": "puzzle-escape-quest-pack", "comedy": "comedy-host-night"}.get(ev["category"])
    if related:
        p = packs_by_slug[related]
        pack_link = (f'<h3>Host this yourself</h3><p>Love the format? The '
                     f'<a href="/packs/{p["slug"]}/">{escape(p["short_title"])} kit</a> (CA${p["price_cad"]}) '
                     f'lets you run this night anywhere.</p>')
    content = f'''<section class="page-hero"><div class="container">
  <p class="eyebrow">{escape(CATS[ev["category"]])} · Kingston, ON</p>
  <h1>{escape(ev["title"])}</h1>
  {sample_notice(ev)}
</div></section>
<section class="section"><div class="container split">
  <div>
    <p class="hero-sub">{escape(ev["description"])}</p>
    <ul class="detail-meta">
      <li><strong>When:</strong> Every {DAY_NAMES[ev["weekday"]]}, {fmt_time(ev["start_time"])} · next on {nxt.strftime("%B %-d")}</li>
      <li><strong>Where:</strong> {escape(ev["venue"]["name"])}, {escape(ev["venue"]["address"])}</li>
      <li><strong>Host:</strong> <a href="/hosts/{host["slug"]}/">{escape(host["name"])}</a></li>
      {price_row}
    </ul>
    <p class="cta-row">{cta}
      <a class="btn btn-ghost" href="/events/on/kingston/">More Kingston events</a></p>
  </div>
  <aside class="panel">
    <h3>Book this host for your venue</h3>
    <p>{escape(host["name"])} — {escape(host["tagline"].lower())}. Typical draw {escape(host["typical_draw"])}.</p>
    <p><a class="btn btn-outline btn-sm" href="/hosts/{host["slug"]}/">View host profile →</a></p>
    {pack_link}
  </aside>
</div></section>'''
    page(f'/events/{ev["slug"]}/', nav="nav_events",
         title=f'{ev["title"]} | QuestLinq',
         description=ev["description"][:155],
         content=content,
         ld=[event_ld(ev), breadcrumbs(("Home", "/"), ("Events", "/events/on/kingston/"),
                                       (ev["title"], f'/events/{ev["slug"]}/'))])


def hosts_hub_content(hs, heading, sub, active):
    chips = ['<a class="chip%s" href="/hosts/on/kingston/">All hosts</a>' % (" active" if active == "all" else "")]
    for c, label in CATS.items():
        if any(c in h["event_types"] for h in hosts):
            chips.append('<a class="chip%s" href="/hosts/on/kingston/%s/">%s</a>'
                         % (" active" if active == c else "", c, escape(label)))
    cards = "\n".join(host_card(h) for h in hs)
    return f'''<section class="page-hero"><div class="container">
  <p class="eyebrow">Kingston, Ontario</p>
  <h1>{heading}</h1>
  <p class="hero-sub">{sub}</p>
</div></section>
<section class="section"><div class="container">
  <div class="filter-row">{''.join(chips)}</div>
  <div class="card-grid">
{cards}
  </div>
  <p class="section-more footnote">Browsing is free. When you find your host, connect for a flat
  CA${site["connect_price_cad"]} — <a href="/for-venues/">how it works</a>.</p>
</div></section>'''


def build_hosts():
    hub = f'/hosts/{CITY["province"]}/{CITY["slug"]}/'
    page(hub, nav="nav_hosts",
         title="Event hosts in Kingston — book trivia, mystery & comedy nights | QuestLinq",
         description="Browse Kingston's event hosts free: trivia crews, murder mystery masters, comedy MCs, "
                     "karaoke hosts. Connect for a flat CA$29 when you're ready to book.",
         content=hosts_hub_content(hosts, "Find your event host",
                                   "Vetted hosts who fill rooms. Browse free — profiles show media, pricing "
                                   "guidance, availability, and reviews.", "all"),
         ld=[breadcrumbs(("Home", "/"), ("Hosts", hub))])
    for cat, label in CATS.items():
        hs = [h for h in hosts if cat in h["event_types"]]
        if not hs:
            continue
        page(hub + cat + "/", nav="nav_hosts",
             title=f"{label} hosts in Kingston — hire for your venue | QuestLinq",
             description=f"Hire a {label.lower()} host in Kingston, Ontario. Browse profiles free; "
                         f"connect for a flat CA$29.",
             content=hosts_hub_content(hs, f"{escape(label)} hosts in Kingston",
                                       f"Hosts who run {escape(label.lower())} nights.", cat),
             ld=[breadcrumbs(("Home", "/"), ("Hosts", hub), (label, hub + cat + "/"))])
    for h in hosts:
        build_host_detail(h)


def build_host_detail(h):
    types = " · ".join(CATS[t] for t in h["event_types"])
    days = ", ".join(DAY_NAMES[d][:3] for d in h["availability"])
    quotes = "".join(f'<blockquote>“{escape(t["quote"])}”</blockquote><p class="case-source">— {escape(t["author"])}, {escape(t["venue"])}</p>'
                     for t in h["testimonials"])
    their_events = [e for e in events if e["host_slug"] == h["slug"]]
    ev_list = "".join(f'<li><a href="/events/{e["slug"]}/">{escape(e["title"])}</a> — every {DAY_NAMES[e["weekday"]]}</li>'
                      for e in their_events)
    ev_html = f"<h3>Currently running</h3><ul>{ev_list}</ul>" if ev_list else ""
    verified = ' <span class="badge badge-gold">Verified</span>' if h.get("verified") else ""
    connect_url = f'{site["lemon_store"]}/checkout?product={site["lemon_connect_product"]}&host={h["slug"]}'
    content = f'''<section class="page-hero"><div class="container">
  <p class="eyebrow">{escape(types)} · Kingston, ON</p>
  <h1>{escape(h["name"])}{verified}</h1>
  <p class="hero-sub">{escape(h["tagline"])}</p>
  {sample_notice(h)}
</div></section>
<section class="section"><div class="container split">
  <div>
    <p>{escape(h["bio"])}</p>
    <ul class="detail-meta">
      <li><strong>Event types:</strong> {escape(types)}</li>
      <li><strong>Experience:</strong> {h["years_experience"]} years</li>
      <li><strong>Typical draw:</strong> {escape(h["typical_draw"])}</li>
      <li><strong>Pricing guidance:</strong> ${h["pricing_guidance"]["from_cad"]}–${h["pricing_guidance"]["to_cad"]} CAD {escape(h["pricing_guidance"]["unit"])}</li>
      <li><strong>Usually available:</strong> {days}</li>
      <li><strong>Service area:</strong> Kingston + {h["service_radius_km"]} km</li>
      <li><strong>Venue needs:</strong> {escape(h["requirements"])}</li>
    </ul>
    {quotes}
    {ev_html}
  </div>
  <aside class="panel connect-box">
    <h3>Book {escape(h["name"])} for your venue</h3>
    <p class="price">CA${site["connect_price_cad"]}</p>
    <p>One flat fee for a warm introduction — contact details, availability check, and intro
    email, usually same day. No commission on your booking.</p>
    <p><a class="btn btn-gold" href="{connect_url}">Connect with this host</a></p>
    <p class="footnote">You'll book and pay the host directly. Introductions are covered by our
    <a href="/refunds/">hassle-free guarantee</a> — host unresponsive, money back.</p>
  </aside>
</div></section>'''
    ld = {
        "@context": "https://schema.org", "@type": "PerformingGroup",
        "name": h["name"], "description": h["bio"],
        "areaServed": "Kingston, Ontario",
        "url": DOMAIN + f'/hosts/{h["slug"]}/',
        "knowsAbout": [CATS[t] for t in h["event_types"]],
    }
    page(f'/hosts/{h["slug"]}/', nav="nav_hosts",
         title=f'{h["name"]} — {types} host in Kingston | QuestLinq',
         description=f'{h["tagline"]}. {h["bio"][:120]}',
         content=content,
         ld=[ld, breadcrumbs(("Home", "/"), ("Hosts", "/hosts/on/kingston/"),
                             (h["name"], f'/hosts/{h["slug"]}/'))])


def build_packs():
    cards = "\n".join(pack_card(p) for p in packs if p["tier"] != "bundle")
    bundles = "\n".join(pack_card(p) for p in packs if p["tier"] == "bundle")
    content = f'''<section class="page-hero"><div class="container">
  <p class="eyebrow">Printable host kits</p>
  <h1>A great night, in a PDF</h1>
  <p class="hero-sub">Download, print, host. Murder mysteries, tavern nights, puzzle quests and more —
  built for bars, breweries, and living rooms. Every kit is covered by
  <a href="/refunds/">14-Day Hassle-Free Returns</a>.</p>
</div></section>
<section class="section"><div class="container">
  <div class="card-grid">
{cards}
  </div>
  <h2 class="section-title" style="margin-top:1.6em">Bundles — the best value</h2>
  <div class="card-grid">
{bundles}
  </div>
</div></section>'''
    page("/packs/", nav="nav_packs",
         title="Printable party & event host kits | QuestLinq Host Packs",
         description="Printable host kits for murder mystery nights, fantasy tavern parties, puzzle quests, "
                     "team-building and more. Instant download, 14-day hassle-free returns.",
         content=content,
         ld=[breadcrumbs(("Home", "/"), ("Host Packs", "/packs/"))])
    for p in packs:
        build_pack_detail(p)


def build_pack_detail(p):
    includes = "".join(f"<li>{escape(x)}</li>" for x in p["includes"])
    who = " · ".join(escape(x) for x in p["who"])
    uses = " · ".join(escape(x) for x in p["use_cases"])
    upsell_cards = "\n".join(pack_card(packs_by_slug[s]) for s in p["upsells"] if s in packs_by_slug)
    buy_url = f'{site["lemon_store"]}/checkout?product={p["lemon_slug"]}'
    badge = f'<span class="badge badge-teal">{escape(p["badge"])}</span>' if p.get("badge") else ""
    content = f'''<section class="page-hero"><div class="container">
  <p class="eyebrow">Host pack · Instant download {badge}</p>
  <h1>{escape(p["short_title"])}</h1>
  <p class="hero-sub">{escape(p["tagline"])}</p>
</div></section>
<section class="section"><div class="container split">
  <div>
    <p>{escape(p["description"])}</p>
    <h2>What's included</h2>
    <ul class="checklist">{includes}</ul>
    <ul class="detail-meta">
      <li><strong>Made for:</strong> {who}</li>
      <li><strong>Perfect for:</strong> {uses}</li>
      <li><strong>Format:</strong> Printable PDF, instant download</li>
    </ul>
  </div>
  <aside class="panel connect-box">
    <p class="price">CA${p["price_cad"]}</p>
    <p><a class="btn btn-gold" href="{buy_url}">Buy &amp; download</a></p>
    <p class="footnote">Secure checkout via Lemon Squeezy ·
    <a href="/refunds/">14-Day Hassle-Free Returns</a> · License: personal, private event, or
    single-venue use (<a href="/terms/">terms</a>).</p>
  </aside>
</div></section>
<section class="section"><div class="container">
  <h2 class="section-title">Pairs well with</h2>
  <div class="card-grid">
{upsell_cards}
  </div>
</div></section>'''
    ld = {
        "@context": "https://schema.org", "@type": "Product",
        "name": p["title"], "description": p["description"],
        "image": DOMAIN + "/assets/img/gold-shield-primary.png",
        "brand": {"@type": "Brand", "name": "QuestLinq"},
        "offers": {"@type": "Offer", "priceCurrency": "CAD", "price": p["price_cad"],
                   "availability": "https://schema.org/InStock",
                   "url": DOMAIN + f'/packs/{p["slug"]}/'},
    }
    page(f'/packs/{p["slug"]}/', nav="nav_packs",
         title=f'{p["title"]} | QuestLinq',
         description=f'{p["tagline"]} {p["description"][:110]}',
         content=content,
         ld=[ld, breadcrumbs(("Home", "/"), ("Host Packs", "/packs/"),
                             (p["short_title"], f'/packs/{p["slug"]}/'))])


def build_static_pages():
    page("/for-venues/", nav="nav_venues",
         title="Fill your dead nights — find event hosts in Kingston | QuestLinq for Venues",
         description="Browse Kingston event hosts free. Trivia, murder mystery, comedy, karaoke — "
                     "connect for a flat CA$29 and book direct. No agency retainers, no commission.",
         content=tpl("for-venues.html"),
         ld=[breadcrumbs(("Home", "/"), ("For Venues", "/for-venues/"))])
    page("/become-a-host/", nav="nav_host",
         title="Become an event host — get booked by venues, never pay for leads | QuestLinq",
         description="List your hosting act free on QuestLinq. Venues pay to reach you; you keep 100% "
                     "of your booking fee. Kingston, Ontario and expanding.",
         content=tpl("become-a-host.html"),
         ld=[breadcrumbs(("Home", "/"), ("Become a Host", "/become-a-host/"))])
    page("/about/",
         title="About QuestLinq — Connecting People Through Play",
         description="QuestLinq connects venues with event hosts, guests with event nights, and party-throwers "
                     "with printable host kits. Born behind the mic in Kingston, Ontario.",
         content=tpl("about.html"), og_image="/assets/img/about-us-collage.png",
         ld=[breadcrumbs(("Home", "/"), ("About", "/about/"))])
    page("/terms/", title="Terms & Conditions | QuestLinq",
         description="QuestLinq terms of use: digital products, 14-day hassle-free returns, usage license, "
                     "event responsibility, and liability.",
         content=tpl("terms.html"))
    page("/refunds/", title="14-Day Hassle-Free Returns | QuestLinq",
         description="Not happy with a QuestLinq purchase? Tell us within 14 days and we'll refund you — "
                     "no interrogation, no hoops.",
         content=tpl("refunds.html"))
    page("/404.html", title="Page not found | QuestLinq",
         description="This page has moved on.", content=tpl("404.html"))


def build_meta_files():
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    today = date.today().isoformat()
    urls = "\n".join(
        f"  <url><loc>{DOMAIN}{p}</loc><lastmod>{today}</lastmod></url>" for p in sorted(set(SITEMAP)))
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n")


def main():
    build_assets()
    build_home()
    build_events()
    build_hosts()
    build_packs()
    build_static_pages()
    build_meta_files()
    n_pages = len(list(OUT.rglob("*.html")))
    print(f"Built {n_pages} pages → {OUT}")


if __name__ == "__main__":
    main()
