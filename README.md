# Awestruck Today

*Every day, a true story of what God did through ordinary, flawed people to shape the world.*

This repo builds awestrucktoday.org: one sourced "On This Day in Christian History" entry a day.

## How it works

- `content/entries/` holds one JSON file per **approved** entry (Status Verified or later in the Entry Database). Drafts, review notes and anything unapproved never go here, because this repo is public.
- `scripts/build.mjs` builds the site into `site/`. It publishes only entries whose date has arrived in **Eastern time**, so each page goes public at midnight Eastern on its date. `/today` always points at the current entry.
- `.github/workflows/deploy.yml` runs the build on every push and just after midnight Eastern every day, then deploys to GitHub Pages.
- `scripts/test-build.mjs` checks the release rule (time zone rollover, future and unapproved entries stay hidden). The deploy stops if it fails.

Run locally: `node scripts/test-build.mjs && node scripts/build.mjs`

## Social assets

- `.github/workflows/build-entry.yml` runs when an entry file is added or changed. It downloads each listed image **only if its license is on the free-to-use list** (public domain, CC0, no known restrictions, CC BY, CC BY-SA), saves it with its credits to `assets/<ID>/` (the rights log), and renders the carousel slides and lock screen.
- `renderer/render.py` holds the brand templates (HTML rendered to PNG); `scripts/fetch_media.py` does the license-checked downloads; `fonts/` holds Instrument Serif (SIL Open Font License).
- The entry format is being unified between the site build and the renderer before the first batch.

## Rights

All rights reserved. This repo has no open-source or Creative Commons license on purpose: some quoted Bible translations (ESV) may not appear in Creative Commons–licensed publications. Archival images are used under their own licenses, credited on each entry.
