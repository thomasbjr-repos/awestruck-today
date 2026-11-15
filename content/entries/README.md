# Entries

One JSON file per **approved** entry, named `YYYY-MM-DD-short-name.json`. Only entries Thomas has set to Verified (or later) belong here; this folder is public, so never commit drafts or review notes.

The site builds an entry page only once its `date` has arrived in Eastern time, at `/MM-DD/slug/`.

## Required

| Field | Example |
| --- | --- |
| `date` | `"2026-11-28"` (the publish date, YYYY-MM-DD) |
| `slug` | `"augustine-of-hippo"` (lowercase letters, digits, hyphens) |
| `title` | `"The professor who told God \"not yet\""` |
| `person` | `"Augustine of Hippo"` |
| `theme` | One of the seven weekday themes, spelled exactly as in the Concept Brief (e.g. `"Science, Education & Thinkers"`). Holy-day entries keep their weekday's theme. |
| `status` | `"Verified"`, `"Produced"`, `"Scheduled"` or `"Published"` (anything else is never built) |

## Optional (each section appears only when present)

Text fields may use `*asterisks*` for italics; everything else is shown as plain text.

```json
{
  "hook": "He ran from God for half his life. Then a child chanted two words: *Take up and read.*",
  "dateline": "Augustine of Hippo · Born on this day, November 13, 354 · Thagaste, North Africa",
  "summary": "One-line description for search results and link previews.",
  "holy_day": "Christmas Day",
  "window": false,
  "event_date": "2026-11-09",
  "lead_image": {
    "src": "/assets/AT-11-13-SCI-augustine/lead.jpg",
    "srcset": "/assets/AT-11-13-SCI-augustine/lead-800.jpg 800w, /assets/AT-11-13-SCI-augustine/lead-1600.jpg 1600w",
    "alt": "Botticelli's fresco of Augustine at his desk, looking up from his books",
    "credit": "Sandro Botticelli, *St Augustine in His Study*, c. 1480 · Public domain, via Wikimedia Commons",
    "focus": "50% 30%"
  },
  "numbers": [
    { "value": "93", "prefix": "", "meaning": "of his own works, reviewed one by one at 72", "as_of": "c. 427", "tier": "B", "source_short": "Augustine, *Retractations*" },
    { "value": "1,030", "prefix": "about", "meaning": "writings counted by Possidius", "as_of": "c. 435", "tier": "B", "reported": true }
  ],
  "story": [
    "First paragraph (gets the drop cap; states the anniversary).",
    { "quote": "Thou madest us for Thyself…", "cite": "Augustine, *Confessions* I.1, trans. Pusey, 1838 · Tier A" },
    "Next paragraph…"
  ],
  "quote": { "text": "…", "source": "…", "tier": "A" },
  "scripture": { "text": "…", "ref": "Romans 13:13–14", "translation": "BSB", "note": "the verses he read in the garden" },
  "scripture_credits": ["Full credit line for any copyrighted translation quoted on the page"],
  "youtube_id": "the Short's video id",
  "extras": [ { "type": "GALLERY", "title": "…", "url": "https://…", "credit": "Public domain · Wikimedia Commons" } ],
  "why": "Why It Matters Today, two or three sentences.",
  "why_reel_line": "One sentence drawn from `why`, for the reel's Why It Matters card.",
  "ask_yourself": "What's the \"not yet\" I've been saying to God?",
  "sources": [ { "text": "Augustine, *De beata vita* 1.6 (386)", "tier": "A", "url": "https://…" } ],
  "confidence": "Confidence note for anything traditional or disputed."
}
```

- `window: true` stamps the entry "THIS WEEK" (the ±3-day rule); give the real event date in `event_date`.
- `numbers`: 1–3 figures; the first is the headline figure on the homepage. Never a Tier C figure first.
- `quote` is used when no `{ "quote": … }` item sits inside `story`; the homepage also shows it.
- `why` is about **60 words or fewer**: it is printed word for word on its own tile in every social post, so the paragraph itself is shortened rather than cut down for the tile. `why_reel_line` is one sentence of **18 words or fewer**, drawn from it, for the reel card (about 4 seconds).
- `ask_yourself` (renamed from `prompt` on Nov 14, 2026) is **one question in the first person** — "I", "my", "me", never "you" — of **14 words or fewer**: answerable, no yes/no, no comparison with the person in the story. It shows as a card on the entry page, and as its own tile and reel card on every social post. Entries that still use `prompt` render in the same card.
- Older entries with a single `html` field still render.
