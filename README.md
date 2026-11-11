# Awestruck Today

*Every day, a true story of what God did through ordinary, flawed people to shape the world.*

Private working repo for the Awestruck Today pipeline: card renderer, license-checked media and, next, the website.

## How it works

1. Claude drafts an entry, Thomas reviews it in its Claude Doc, and its row in the Entry Database is set to **Verified**.
2. Claude adds the entry's data file to `entries/` (e.g. `entries/2026-11-11-anne-steele.json`).
3. The **Build entry assets** action runs on its own:
   - downloads the Instrument Serif font (free, OFL) once;
   - downloads each image listed under `media` **only if its license is on the auto-OK list** (CC0, public domain, no known restrictions, CC BY, CC BY-SA), reading Wikimedia Commons licenses from the Commons API. Anything else is skipped and reported as ⚠;
   - renders the carousel slides and lock screen;
   - saves cleared images and their credits to `assets/<ID>/` and offers the rendered cards as a download on the run's page.

## Folders

| Folder | Holds |
| --- | --- |
| `entries/` | One JSON data file per entry |
| `renderer/` | `render.py`: brand templates (HTML) to PNG |
| `scripts/` | `fetch_media.py`: license-checked image downloads |
| `assets/<ID>/` | Cleared images plus `credits.json` (the rights log) |
| `fonts/` | Brand fonts (added by the action) |

The website (`site/`) comes next and will be published with Cloudflare Pages.
