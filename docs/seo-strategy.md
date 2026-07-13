# QuestLinq — SEO Strategy

The organic-search plan for winning "…near me" and "things to do" queries, city by city, starting with Kingston, Ontario. Static pages on Cloudflare Pages are ideal for this: fast, crawlable, no JS required to render content.

---

## 1. The Prize

For local event queries, Google shows an **event carousel** above the regular results (fed by schema.org `Event` markup) plus the local pack. Eventbrite and AllEvents live off this surface, but their Kingston inventory is thin and stale. A site with **denser, fresher, better-structured Kingston inventory** can own both the carousel and the organic results locally — and repeat the trick per city.

## 2. Query Targets (five guest intents + two B2B surfaces)

| Intent | Example queries | Landing page |
|---|---|---|
| Time-bound | "things to do in kingston tonight", "kingston events this weekend" | `/events/on/kingston/tonight`, `/…/this-weekend` |
| Category + local | "murder mystery near me", "comedy night kingston", "trivia tonight kingston" | `/events/on/kingston/murder-mystery` etc. |
| Occasion | "bachelorette party ideas kingston", "team building activities kingston", "birthday ideas for adults" | Occasion guides (see §5) |
| Seasonal | "halloween events kingston", "new years eve kingston" | Seasonal hubs, published 6–8 weeks early |
| Free | "free events kingston this weekend" | `/events/on/kingston/free` |
| **Venue (B2B)** | "hire trivia host kingston", "event ideas for bars", "how to get more customers on weeknights" | `/hosts/on/kingston/{type}`, `/for-venues`, guides |
| **Host/buyer (DTC)** | "printable murder mystery kit", "how to host a murder mystery at a bar" | `/packs/{slug}`, how-to guides |

Note "near me" queries are served by *geo-relevance*, not by pages containing the words "near me": Google resolves them to the searcher's city. The way to win them is city-scoped pages with real local inventory + `Event`/`LocalBusiness` markup + fast pages.

## 3. URL Architecture (scales to every future city with zero rework)

```
/events/{province}/{city}/                    city event hub
/events/{province}/{city}/tonight             time-filtered views (indexable)
/events/{province}/{city}/this-weekend
/events/{province}/{city}/free
/events/{province}/{city}/{category}          murder-mystery, comedy, karaoke…
/events/{event-slug}                          event detail
/hosts/{province}/{city}/                     host roster
/hosts/{province}/{city}/{event-type}         "murder mystery hosts in Kingston"
/hosts/{host-slug}                            host profile
/packs/{product-slug}                         product pages
/guides/{slug}                                content/occasion guides
```

Rules: lowercase, hyphenated, no query strings for indexable views, province codes (`on`) for CA/US disambiguation later (Kingston ON vs Kingston NY). Every page declares `rel=canonical`; empty city/category combinations are **not generated** (no thin doorway pages — a page exists only when it has ≥1 real listing).

## 4. Structured Data Plan

| Page | schema.org types |
|---|---|
| Event detail | `Event` (name, startDate, location w/ full `Place`+address, `offers` w/ price & availability, image, performer → host, organizer) |
| City/category hubs | `ItemList` of `Event` |
| Host profile | `Person` or `PerformingGroup` + `Service`, `aggregateRating` once reviews exist |
| Pack product | `Product` + `Offer` (price CAD, digital) |
| Guides | `Article` / `FAQPage` where genuine Q&A exists |
| Sitewide | `Organization` (logo = gold shield, sameAs socials), `BreadcrumbList` |

`Event` markup is the carousel ticket — validate every template with Google's Rich Results test. Recurring events get one page per upcoming occurrence *or* `eventSchedule`, never a wall of duplicate pages.

## 5. Content Layer (guides that feed all three sectors)

Two families, each written once and reusable per city where relevant:

- **Occasion guides (guest-facing, high ticket value):** "Bachelorette Party Ideas in Kingston", "Team Building Activities in Kingston", "Adult Birthday Ideas That Aren't Dinner". Each guide: real local events + relevant hosts + the matching pack ("DIY option"). One guide sells all three sectors.
- **How-to guides (host/venue-facing):** "How to Host a Murder Mystery Night at a Bar" (→ pack + become-a-host), "How to Fill Your Bar on a Tuesday" (→ for-venues), "How Much Does an Event Host Cost?" (→ roster). These intercept the *outcome searches* venues actually type.

## 6. Technical Checklist

- Static HTML, mobile-first, Core Web Vitals green by default (no framework, Cloudflare CDN).
- `sitemap.xml` regenerated on every build (events churn constantly — freshness signals matter); submit in Search Console; `lastmod` accurate.
- OG/Twitter cards on every event/pack page (social shares are an entry point).
- Expired events: keep the URL live with "this event has passed" + links to upcoming similar events (accumulated link equity stays).
- `robots.txt` + canonical hygiene; no indexable duplicate filter permutations.

## 7. City Expansion Playbook

A "city launch" in SEO terms = repeat this checklist (same templates, new data):

1. Seed ≥10 real recurring events + ≥5 host profiles for the city (pages are never thin).
2. Generate the city hub + category pages + `/tonight` `/this-weekend` `/free` views.
3. Publish 3 occasion guides localized to the city.
4. Update sitemap; build 2–3 local citations/links (tourism boards, university event calendars, local press "new site lists everything happening in X").
5. Watch Search Console for the city's queries; iterate titles/descriptions.

## 8. Measurement

- **North star:** organic sessions on city pages → email captures → tickets/connects attributed to organic.
- Search Console: impressions/clicks for "kingston + tonight/this weekend/{category}" clusters; event-carousel impressions (Performance → Search appearance → Events).
- Rank tracking on ~20 core Kingston queries; expand set per city launch.
- Target (assumption): top-3 on core "kingston tonight" cluster within 4–6 months of consistent inventory.
