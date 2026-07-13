# QuestLinq — Deploy Guide (GitHub + Cloudflare)

The site is fully static: `build.py` (Python stdlib, no dependencies) renders `data/*.json` + `templates/` into `public/`, and `public/` is committed — so Cloudflare Pages can serve it with **zero build configuration**.

## 1. Cloudflare Pages setup (one time)

1. Cloudflare dashboard → **Workers & Pages → Create → Pages → Connect to Git** → pick this repo.
2. Production branch: `main` (merge the working branch when ready).
3. Build settings:
   - **Build command:** *(leave empty)* — or `python3 build.py` if you'd rather not commit `public/`
   - **Build output directory:** `public`
4. Deploy. You'll get `<project>.pages.dev` immediately.

## 2. Domain + email

1. Move `questlinq.com` DNS to Cloudflare (if not already).
2. Pages project → **Custom domains** → add `questlinq.com` (and `www` redirect).
3. **Email Routing** (Cloudflare dashboard → Email): create `hello@questlinq.com` → forward to your inbox. The site already uses this address everywhere.

## 3. Editing content (no code needed)

| To change… | Edit… | Then |
|---|---|---|
| Events | `data/events.json` | `python3 build.py`, commit `data/` + `public/` |
| Hosts | `data/hosts.json` | same |
| Packs/prices | `data/packs.json` | same |
| Store URL, connect price, cities | `data/site.json` | same |
| Page copy | `templates/*.html` | same |

Sample listings carry `"sample": true` — set to `false` (or delete the key) once a listing is real, and the "Example listing" badges disappear. Delete the sample entries you don't replace.

## 4. Launch TODOs (site is wired for these, waiting on you)

- [ ] **LemonSqueezy products:** create each product from [host-packs-catalog.md](host-packs-catalog.md), then replace every `TODO-…` value in `data/packs.json` (`lemon_slug`) and `data/site.json` (`lemon_connect_product`) with real product slugs/URLs from `hostlinqpayments.lemonsqueezy.com`. Rebuild.
- [ ] **Host Connect product:** create a CA$29 "Host Connect" product in LemonSqueezy (add a custom field for "Which host?"); fulfil manually with a warm intro email per [product-spec.md](product-spec.md) §3.
- [ ] **Form endpoint:** the become-a-host form posts to `#`. Point it at a Cloudflare Pages Function (`/functions/api/host-apply.js`) or a form service; until then the mailto fallback works.
- [ ] **Ticketing/RSVP:** event CTAs are mailto for MVP; upgrade per product-spec phase 3.
- [ ] **Search Console:** verify the domain, submit `https://questlinq.com/sitemap.xml`, and watch the "Events" search appearance report ([seo-strategy.md](seo-strategy.md) §8).
- [ ] Replace sample hosts/events with real Kingston listings as they sign on.

## 5. Local preview

```bash
python3 build.py
python3 -m http.server -d public 8080
# → http://localhost:8080
```
