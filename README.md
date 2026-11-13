# Awestruck Today

*Every day, a true story of what God did through ordinary, flawed people to shape the world.*

This repo builds awestrucktoday.org: one sourced "On This Day in Christian History" entry a day.

## How it works

The site is built with **[Astro](https://astro.build)** (free) as plain static pages for GitHub Pages, in the "Soft light" design (Brand Guide, "Website: Soft light"): full-bleed images, dark and light mode, phone-first layouts.

- `content/entries/` holds one JSON file per **approved** entry (Status Verified or later in the Entry Database). Drafts, review notes and anything unapproved never go here, because this repo is public. The fields are listed in `content/entries/README.md`.
- `src/lib/entries.mjs` holds the release rule: only approved entries whose date has arrived in **Eastern time** are built, so each page goes public at midnight Eastern on its date. `/today` always points at the current entry.
- `src/pages/` holds the pages: home (`index.astro`), `today`, each entry (`[mmdd]/[slug].astro` → `/MM-DD/short-name/`), `archive` (calendar), `about`, `what-we-believe` and `404`.
- `src/styles/site.css` is the whole design system (the same file as the Website directions canvas). `src/lib/icons.mjs` holds the seven theme icons; `src/lib/brand.mjs` the sunrise mark, headline, channels, analytics token and the MailerLite form address.
- `.github/workflows/deploy.yml` installs Astro, runs the checks, builds and deploys on every push to `main` and just after midnight Eastern every day. Pull requests build a downloadable preview instead of deploying.
- `scripts/test-build.mjs` checks the release rule and builds a test copy of the site (time zone rollover; future and unapproved entries stay hidden; /today, Archive and pages exist). The deploy stops if it fails.

**Previews (Cloudflare Pages, free):** every branch and pull request also builds on Cloudflare Pages (build command `npm run build`, output folder `site`, `NODE_VERSION=22`). Those builds carry a "Preview" badge and a no-index tag; the real site stays on GitHub Pages.

Run locally (needs Node 20+): `npm install`, then `npm run dev` to preview at http://localhost:4321, `npm test` for the checks, `npm run build` for the real build. Pretend it's another day with `AT_TODAY=2026-12-13 npm run dev`.

## Social assets

- `.github/workflows/build-entry.yml` runs when an entry file is added or changed. It downloads each listed image **only if its license is on the free-to-use list** (public domain, CC0, no known restrictions, CC BY, CC BY-SA), saves it with its credits to `assets/<ID>/` (the rights log), and renders the carousel slides and lock screen.
- `renderer/render.py` holds the brand templates (HTML rendered to PNG); `scripts/fetch_media.py` does the license-checked downloads; `fonts/` holds Instrument Serif (SIL Open Font License).
- The entry format is being unified between the site build and the renderer before the first batch.

## Rights

All rights reserved. This repo has no open-source or Creative Commons license on purpose: some quoted Bible translations (ESV) may not appear in Creative Commons–licensed publications. Archival images are used under their own licenses, credited on each entry.
