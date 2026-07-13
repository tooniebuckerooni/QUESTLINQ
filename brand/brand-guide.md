# QuestLinq — Brand Guide

**Primary mark (decided):** the gold/orange shield with the glowing doorway.
**Primary tagline:** *Events That Bring Us Together.*

The doorway is the brand's whole idea: every user walks through a different door — guests into events, venues into a roster of hosts, hosts into paid gigs, buyers into a party in a PDF. Steps lead up to a lit arch: an invitation, not a barrier.

## 1. Logo System

| Mark | Use | Status |
|---|---|---|
| **Gold shield + wordmark** — "Events That Bring Us Together" | Primary: site header, social, product images, favicon source | Original PNG to be added to `logos/`; provisional SVG recreation in this folder |
| Purple/blue chrome shield — "Connect Through Shared Quests" | Secondary: pack/host-facing contexts where gamer energy fits (Fantasy Tavern line, become-a-host) | PNG to be added |
| Warm script collage — "Connecting People Through Play" | About Us page hero only | PNG to be added |

Files in this folder (provisional recreations until the original renders are exported at production sizes):
- `questlinq-mark.svg` — shield-and-doorway emblem
- `questlinq-wordmark.svg` — wordmark + tagline lockup
- `favicon.svg` — simplified doorway-in-shield for browser tabs

## 2. Color Palette (derived from the gold shield mark)

| Token | Hex | Role |
|---|---|---|
| `--ql-gold` | `#F5A623` | Primary brand gold — CTAs, highlights, shield body |
| `--ql-amber` | `#FFC64B` | Gold highlight / hover states |
| `--ql-ember` | `#E8740C` | Deep orange — gradients, active states |
| `--ql-glow` | `#FFE9B8` | Doorway glow — light accents on dark |
| `--ql-royal` | `#6B2FA0` | Purple accent — secondary panels, links on light |
| `--ql-indigo` | `#2B1B4D` | Deep indigo — dark surfaces |
| `--ql-night` | `#161022` | Near-black background (the "night sky") |
| `--ql-teal` | `#2EC4B6` | The "LINQ" gradient tail — secondary accent, success |
| `--ql-paper` | `#FAF6EE` | Warm off-white for light-mode surfaces/text-on-dark |

Formula: **dark night-sky surfaces, gold leads, purple supports, teal punctuates.** Light mode inverts to `--ql-paper` surfaces with `--ql-indigo` text; gold stays the CTA color in both.

## 3. Typography

- **Display / headings:** bold italic geometric sans with gaming energy (wordmark style). Web-safe route: *Montserrat ExtraBold Italic* (Google Fonts) — closest free match to the logotype; self-host the woff2.
- **Body:** *Inter* (or system stack `-apple-system, Segoe UI, Roboto, sans-serif`) — the marketplace must read clean and trustworthy, not gamer.
- Wordmark treatment: "QUEST" in gold gradient, "LINQ" in teal gradient, always italic, never re-set in body type.

## 4. Voice

- Lead voice is the **gold shield's**: warm, adventurous, inclusive — "Events That Bring Us Together."
- Site copy leans *pub-social* over *esports*: "Find something to do tonight," "Fill your dead nights," "You never pay for leads."
- The quest/fantasy flavor concentrates where the audience wants it (Fantasy Tavern, packs, host community); it stays subtle on venue-facing pages.

## 5. Usage Rules

- The shield always sits on dark (`--ql-night`) or photography; never on white without its dark container.
- Minimum clear space: half the shield's width on all sides. Don't stretch, recolor, or drop-shadow beyond the built-in glow.
- Taglines pair only as set here (gold ↔ "Events That Bring Us Together"); don't mix lockups.
- Product/pack imagery: one visual family per product line (the Mystery line shares a system) — see [host-packs-catalog.md](../docs/host-packs-catalog.md) §5.

## 6. TODO

- [ ] Export the original gold-shield renders (1024px+, transparent-background versions if possible) into `brand/logos/` — see `logos/README.md`.
- [ ] Commission/produce a vector redraw of the final shield for crisp scaling (the provisional SVGs here are stand-ins).
- [ ] Generate favicon.ico + app icons from `favicon.svg` at build time.
