// Builds the static site into ./site from content/entries/*.json.
// Only entries dated on or before "today" in America/New_York are published,
// so each page goes public at midnight Eastern on its date.
//
// Usage: node scripts/build.mjs [--today YYYY-MM-DD] [--content DIR] [--out DIR]
// Env:   BASE_PATH  path prefix when served from a subfolder (e.g. "/awestruck-today")

import { readdir, readFile, mkdir, writeFile, rm } from 'node:fs/promises';
import { join } from 'node:path';

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, cur, i, arr) => {
    if (cur.startsWith('--')) acc.push([cur.slice(2), arr[i + 1]]);
    return acc;
  }, [])
);

const BASE = (process.env.BASE_PATH || '').replace(/\/$/, '');
const CONTENT = args.content || 'content/entries';
const OUT = args.out || 'site';
const TZ = 'America/New_York';

export function todayInEastern(now = new Date()) {
  // en-CA formats as YYYY-MM-DD
  return new Intl.DateTimeFormat('en-CA', { timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit' }).format(now);
}

const TODAY = args.today || todayInEastern();

const esc = (s = '') => String(s)
  .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;').replaceAll("'", '&#39;');

const THEMES = {
  'Preachers & Sermons': '#F2994A',
  'Missions & Movements': '#3FB6A8',
  'Books & Writings': '#E06C74',
  'Music & Hymns': '#A48CF0',
  'Arts & Film': '#5B8DEF',
  'Science, Education & Thinkers': '#8FD6E8',
  'Entrepreneurs & Builders': '#9DBF5A',
};

const HEADLINE = 'Every day, a true story of what God did through ordinary, flawed people to shape the world.';

function page({ title, body, description = HEADLINE, accent = '#E9C77B', noindex = false }) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description)}">
${noindex ? '<meta name="robots" content="noindex">\n' : ''}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{--night:#0B0F14;--panel:#121821;--line:#222B38;--ivory:#F1EEE8;--mist:#C4C9D2;--slate:#8A93A3;--gold:#E9C77B;--accent:${accent}}
*{box-sizing:border-box}
html,body{margin:0;background:var(--night);color:var(--ivory);font:400 18px/1.6 Inter,system-ui,sans-serif}
a{color:var(--gold)}
.wrap{max-width:720px;margin:0 auto;padding:32px 24px 64px}
header{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid var(--line);padding-bottom:16px}
.mark{font:400 30px/1 'Instrument Serif',Georgia,serif;color:var(--ivory);text-decoration:none}
.mark em{color:var(--gold)}
.stamp{font:500 13px/1 Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
h1{font:400 clamp(40px,8vw,64px)/1.05 'Instrument Serif',Georgia,serif;margin:40px 0 16px}
h1 em{color:var(--accent)}
.dateline{color:var(--mist);font-size:16px;border-left:3px solid var(--accent);padding-left:12px}
.headline{color:var(--mist);font-size:16px;margin-top:8px}
footer{margin-top:64px;border-top:1px solid var(--line);padding-top:16px;color:var(--slate);font-size:14px}
</style>
</head>
<body><div class="wrap">
<header><a class="mark" href="${BASE}/">Awestruck <em>Today</em></a></header>
<p class="headline">${esc(HEADLINE)}</p>
${body}
<footer>© Awestruck Today. Every date, quote and number is sourced and tiered.</footer>
</div></body></html>
`;
}

async function loadEntries() {
  let files = [];
  try { files = (await readdir(CONTENT)).filter(f => f.endsWith('.json')); } catch { return []; }
  const entries = [];
  for (const f of files) {
    const e = JSON.parse(await readFile(join(CONTENT, f), 'utf8'));
    for (const k of ['date', 'slug', 'title', 'person', 'theme', 'status']) {
      if (!e[k]) throw new Error(`${f}: missing "${k}"`);
    }
    if (!/^\d{4}-\d{2}-\d{2}$/.test(e.date)) throw new Error(`${f}: date must be YYYY-MM-DD`);
    if (!/^[a-z0-9-]+$/.test(e.slug)) throw new Error(`${f}: slug must be lowercase letters, digits, hyphens`);
    entries.push(e);
  }
  return entries;
}

export function publishable(entries, today) {
  // Only approved entries whose date has arrived (Eastern). Status is set from the Sheet.
  const ok = new Set(['Verified', 'Produced', 'Scheduled', 'Published']);
  return entries
    .filter(e => ok.has(e.status) && e.date <= today)
    .sort((a, b) => a.date.localeCompare(b.date));
}

const mmdd = d => d.slice(5);
const entryPath = e => `/${mmdd(e.date)}/${e.slug}/`;
const longDate = d => new Date(d + 'T12:00:00Z').toLocaleDateString('en-US', { timeZone: 'UTC', month: 'long', day: 'numeric', year: 'numeric' });

async function put(rel, html) {
  const dir = join(OUT, rel);
  await mkdir(dir, { recursive: true });
  await writeFile(join(dir, 'index.html'), html);
}

async function main() {
  const all = await loadEntries();
  const live = publishable(all, TODAY);
  await rm(OUT, { recursive: true, force: true });
  await mkdir(OUT, { recursive: true });

  for (const e of live) {
    const accent = THEMES[e.theme] || '#E9C77B';
    const d = e.date.slice(8);
    const stamp = `ON THIS DAY · ${new Date(e.date + 'T12:00:00Z').toLocaleDateString('en-US', { timeZone: 'UTC', month: 'short' }).toUpperCase()} ${Number(d)}`;
    const body = `
<p class="stamp" style="margin-top:32px">${esc(stamp)}</p>
<h1>${esc(e.title)}</h1>
<p class="dateline">${esc(e.dateline || `${e.person} · ${longDate(e.date)}`)}</p>
${e.html || ''}`;
    await put(entryPath(e), page({ title: `${e.title} — Awestruck Today`, body, accent, description: e.summary || HEADLINE }));
  }

  const latest = live.at(-1);
  const todays = live.filter(e => e.date === TODAY).at(-1);

  // /today → today's entry; before launch (or on a missed day) → most recent entry, else home.
  const target = todays || latest;
  const todayUrl = target ? `${BASE}${entryPath(target)}` : `${BASE}/`;
  await put('today', `<!DOCTYPE html><meta charset="utf-8"><meta name="robots" content="noindex"><title>Today — Awestruck Today</title><meta http-equiv="refresh" content="0; url=${todayUrl}"><link rel="canonical" href="${todayUrl}"><a href="${todayUrl}">Today's story</a>`);

  const home = latest
    ? `<h1>Today's story</h1><p><a href="${BASE}${entryPath(target)}">${esc(target.title)}</a></p>`
    : `<h1>Launching <em>Saturday, November 28, 2026</em></h1>
<p>One true story every day of what God did through one ordinary, flawed person, with every date, quote and number sourced.</p>`;
  await writeFile(join(OUT, 'index.html'), page({ title: 'Awestruck Today', body: home }));
  await writeFile(join(OUT, '404.html'), page({ title: 'Not found — Awestruck Today', body: `<h1>Page not found</h1><p><a href="${BASE}/today/">Go to today's story</a></p>`, noindex: true }));
  await writeFile(join(OUT, '.nojekyll'), '');

  console.log(`Built ${live.length} of ${all.length} entries for ${TODAY} (Eastern) into ${OUT}/`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(err => { console.error(err.message); process.exit(1); });
}
