<p align="center">
  <img src="brand/questlinq-mark.svg" width="140" alt="QuestLinq shield">
</p>

<h1 align="center">QuestLinq</h1>
<p align="center"><em>Events That Bring Us Together.</em></p>

**QuestLinq.com** is a three-sided platform for live social events, launching in **Kingston, Ontario** and expanding outward (Ontario → Canada → USA). It expands laterally from Fat City Entertainment: Fat City is a host; QuestLinq is the marketplace.

## The three revenue sectors

| | Sector | Model |
|---|---|---|
| 🎟 | **Guests** find free & ticketed events | "…near me" SEO + ticketing fee (~5% + $0.79) |
| 🏠 | **Venues** find & book event hosts *(priority)* | Free browse → pay ~$29 to connect, or Venue Pro ~$59/mo |
| 📦 | **Hosts & party-throwers** buy printable host packs | LemonSqueezy digital downloads, CA$9–49 + bundles |

The flywheel: packs recruit hosts and plant QR signage in venues → hosts pitch venues with their QuestLinq profiles → venues pay to connect and book event nights → event pages win "near me" searches → guests buy tickets, join the list, and buy packs.

## Repository map

| Path | Contents |
|---|---|
| [`docs/business-plan.md`](docs/business-plan.md) | Mission, sectors, flywheel, pricing, competition, Kingston launch plan, KPIs |
| [`docs/product-spec.md`](docs/product-spec.md) | Roles & journeys, host-listing schema, connect flow, ticketing, site map, phased build |
| [`docs/seo-strategy.md`](docs/seo-strategy.md) | "Near me" SEO architecture, schema.org plan, city-expansion playbook |
| [`docs/host-packs-catalog.md`](docs/host-packs-catalog.md) | 11-SKU catalog with LemonSqueezy-ready listings, forecast ranking, bundles |
| [`docs/legal/`](docs/legal/terms-and-conditions.md) | Terms & Conditions + 14-Day Hassle-Free Returns refund policy |
| [`docs/deploy.md`](docs/deploy.md) | Cloudflare Pages deploy guide + launch TODOs |
| [`brand/`](brand/brand-guide.md) | Brand guide, palette, SVG marks, original logo renders |
| [`data/`](data/) | Site config, hosts, events, packs — **edit these to change content** |
| [`templates/`](templates/) + [`build.py`](build.py) | Page templates and the stdlib-only generator |
| [`public/`](public/) | The generated site Cloudflare Pages serves (committed) |

## Stack

Plain **HTML/CSS/JS**, this **GitHub** repo, deployed via **Cloudflare Pages** (questlinq.com DNS on Cloudflare). Store checkout via **LemonSqueezy**. Dynamic features (accounts, instant connect-unlock, native ticketing) arrive later on Cloudflare Workers/KV/D1 — no platform migration.

## Status

**MVP site built.** `python3 build.py` renders `data/` + `templates/` into `public/` — deploy per [`docs/deploy.md`](docs/deploy.md). Sample Kingston listings are labeled in `data/`; LemonSqueezy product URLs are `TODO-` placeholders until the products exist (checklist in the deploy guide).
