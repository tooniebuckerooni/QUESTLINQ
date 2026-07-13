# QuestLinq — Product Specification

Static-first product spec for QuestLinq.com. Stack: **plain HTML/CSS/JS in this GitHub repo, deployed on Cloudflare Pages** (questlinq.com DNS on Cloudflare). Dynamic features arrive later via Cloudflare Workers/KV/D1 — no platform migration, ever. Business context in [business-plan.md](business-plan.md).

---

## 1. Roles & Journeys

| Role | Arrives via | Wants | Pays for |
|---|---|---|---|
| **Guest** | "near me" search, social ticket links, in-venue QR signage | Something to do tonight / an event for an occasion | Tickets (fee to QuestLinq) |
| **Venue** | Outcome searches, host pitches, rival-venue FOMO | A packed weeknight without hunting Facebook groups | Connect unlock (~CA$29) or Venue Pro (~CA$59/mo) |
| **Host** | "how to host X" content, pack PDFs, attended events | Paid gigs, a professional profile, tools | Nothing at launch (packs optionally) |
| **Pack buyer** | Product searches, Etsy/Pinterest-style discovery | A great party in a PDF | Packs (CA$9–49, LemonSqueezy) |

### Core journeys
- **Guest:** lands on city/event page → filters (tonight/weekend, category, free/ticketed) → event detail → RSVP (free, email captured) or buy ticket → digest signup.
- **Venue:** lands on `/for-venues` or a host profile → browses roster free (all profile content visible **except** contact/booking) → clicks "Connect with this host" → pays → receives intro → books directly with host. Second unlock triggers Pro pitch.
- **Host:** lands on `/become-a-host` → submits profile (form) → QuestLinq reviews/publishes → host shares profile link as their pitch tool → receives venue intros.
- **Pack buyer:** product page → LemonSqueezy overlay checkout → PDF (which contains the host-recruitment page + venue signage).

## 2. Host Listing Schema (the core asset — Sector C)

Designed around how venues search: **event type × location × budget × availability**, with proof.

```json
{
  "id": "kingston-mystery-mike",
  "name": "Mystery Mike Events",
  "tagline": "Murder mystery nights that pack the room",
  "city": "kingston", "province": "on",
  "service_radius_km": 50,
  "event_types": ["murder-mystery", "trivia", "game-show"],
  "bio": "…",
  "years_experience": 6,
  "media": { "photos": ["…"], "video_url": "…" },
  "pricing_guidance": { "from_cad": 250, "to_cad": 450, "unit": "per event" },
  "availability": ["tue", "wed", "thu"],
  "testimonials": [ { "quote": "…", "author": "…", "venue": "…" } ],
  "verified": true,
  "typical_draw": "30-60 guests",
  "requirements": "PA system, 2 tables",
  "contact": { "email": "…", "phone": "…" }   // NEVER rendered publicly — unlock only
}
```

Notes:
- `contact` is the paywalled field. Everything else is public — the profile must be *fully* convincing before the wall.
- `typical_draw` and `testimonials` are the venue-FOMO fields; profile review nudges hosts to fill them.
- `pricing_guidance` is a range, not a quote — keeps negotiation host↔venue, keeps us out of it.
- Each profile page carries schema.org `Person`/`PerformingGroup` + `Service` markup (see [seo-strategy.md](seo-strategy.md)).

## 3. Venue Connect Flow (the money moment)

**MVP (manual fulfillment — ship this first):**
1. Venue clicks **"Connect with this host — CA$29"** on a profile.
2. Checkout via a LemonSqueezy product ("Host Connect") with the host's name passed in a custom field. *(Reuses the existing store — no payment code to build.)*
3. LemonSqueezy purchase email notifies us → we send a warm intro email to both parties within hours, including the host's one-pager.
4. Follow-up email a week later: "Did you book? Here's Venue Pro."

**v2 (Workers/D1):** authenticated venue accounts, instant unlock (contact revealed + intro email automated), Pro subscription via LemonSqueezy subscriptions, "Host Wanted" gig board with host-side notifications.

Venue-facing pages: `/for-venues` (pitch: case studies with numbers, roster preview, pricing), `/hosts/on/kingston/` (browse/filter), host profile pages.

## 4. Event Listings & Ticketing (Sector B)

**Event record:**

```json
{
  "id": "mystery-night-riverhouse-2026-08-14",
  "title": "Murder Mystery Night at The Riverhouse",
  "host_id": "kingston-mystery-mike",
  "venue": { "name": "The Riverhouse", "address": "…", "city": "kingston", "province": "on" },
  "start": "2026-08-14T19:00-04:00", "end": "…",
  "category": "murder-mystery",
  "price": { "type": "ticketed", "cad": 15 },   // or { "type": "free" }
  "ticket_url": "…", "capacity": 60,
  "image": "…", "description": "…",
  "recurring": "weekly|monthly|null"
}
```

- **MVP:** events stored as JSON/markdown in the repo, pages generated at build time; "tickets" link out (or free RSVP via a form that feeds the email list). Even outbound ticket links build the SEO surface.
- **v2:** native ticketing via Workers + LemonSqueezy/Stripe, ~5% + CA$0.79 fee, QR check-in page.
- Every event page cross-links: host profile ("Book this host for *your* venue"), pack store ("Host this yourself — get the kit"), city page ("More events in Kingston tonight").
- Guest-facing pages: `/events/on/kingston/` (+ `/tonight`, `/this-weekend`, `/free`, per-category) and event detail pages, all with schema.org `Event` markup targeting Google's event carousel.

## 5. Pack Store Integration (Sector A)

- Product pages live on questlinq.com (`/packs/` + `/packs/{slug}`) for SEO; **checkout is LemonSqueezy overlay** (lemon.js) so buyers never leave the page.
- Each product page: hero mockup, what's included, who it's for, FAQ, reviews (later), upsell strip driven by the catalog's upsell paths ([host-packs-catalog.md](host-packs-catalog.md)).
- Every PDF ships with: QuestLinq-branded printable signage w/ QR → `/events/{city}` and a final page → `/become-a-host`.

## 6. Site Map (MVP)

```
/                         Hero: guest event search ("Find something to do tonight" + city)
                          ↓ below fold: venue door ("Fill your dead nights"),
                            host door ("Get booked by venues"), packs strip
/events/on/kingston/      City hub + /tonight /this-weekend /free /{category}
/events/{event-slug}      Event detail (Event markup, tickets/RSVP)
/hosts/on/kingston/       Host roster + /{event-type} filters
/hosts/{host-slug}        Host profile (contact paywalled)
/for-venues               Venue pitch + pricing + case studies
/become-a-host            Host pitch + listing form
/packs/                   Store + /packs/{product-slug}
/about                    Story, Fat City relationship, "Connecting People Through Play"
/terms  /refunds          Legal (docs/legal/)
```

## 7. Phased Build

| Phase | Scope | Infra |
|---|---|---|
| **0 — Static MVP** | All pages above; listings/events as JSON+build script or hand-edited HTML; LemonSqueezy overlay checkout; connect = LemonSqueezy product + manual intro; forms via Cloudflare Pages Functions or form service | GitHub → Cloudflare Pages (free) |
| **1 — Data & search** | Client-side event/host search+filter from JSON index; sitemap automation; digest via email provider | + Pages Functions |
| **2 — Accounts & unlock** | Venue accounts, instant contact unlock, Pro subscription, Host Wanted board | + Workers, D1, KV |
| **3 — Native ticketing** | Ticket sales, fees, QR check-in | + Workers/payments |

## 8. Non-goals (MVP)

- No user-generated content moderation surface (profiles reviewed by hand before publish).
- No host-side fees or featured placement (until demand proven).
- No mobile app; the site is mobile-first responsive.
- No trivia/music-bingo pack products (Fat City non-compete — see catalog).
