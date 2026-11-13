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

const MARK = `<svg class="sun" viewBox="0 0 200 140" fill="none" stroke="#E9C77B" stroke-width="5" stroke-linecap="round" aria-hidden="true"><line x1="125.7" y1="88.4" x2="163.4" y2="83.1"/><line x1="124.2" y1="82.4" x2="153.9" y2="70.6"/><line x1="121.2" y1="77.0" x2="163.6" y2="46.9"/><line x1="117.1" y1="72.4" x2="138.1" y2="48.2"/><line x1="111.9" y1="68.9" x2="135.8" y2="22.7"/><line x1="106.1" y1="66.7" x2="113.7" y2="35.6"/><line x1="100.0" y1="66.0" x2="100.0" y2="14.0"/><line x1="93.9" y1="66.7" x2="86.3" y2="35.6"/><line x1="88.1" y1="68.9" x2="64.2" y2="22.7"/><line x1="82.9" y1="72.4" x2="61.9" y2="48.2"/><line x1="78.8" y1="77.0" x2="36.4" y2="46.9"/><line x1="75.8" y1="82.4" x2="46.1" y2="70.6"/><line x1="74.3" y1="88.4" x2="36.6" y2="83.1"/><path d="M100 63 L103.6 75.4 L116 79 L103.6 82.6 L100 92 L96.4 82.6 L84 79 L96.4 75.4 Z" fill="#E9C77B" stroke="none"/><path d="M24 92 H176"/><path d="M50 105 H150"/><path d="M68 116 H132"/><path d="M86 127 H114"/></svg>`;

// Monogram (profile picture / favicon), from the Logo marks canvas.
const RAYS = Array.from({ length: 24 }, (_, i) => {
  const a = i * Math.PI / 12, r2 = i % 2 ? 76 : 84;
  const f = n => n.toFixed(1);
  return `<line x1="${f(100 + 60 * Math.cos(a))}" y1="${f(100 + 60 * Math.sin(a))}" x2="${f(100 + r2 * Math.cos(a))}" y2="${f(100 + r2 * Math.sin(a))}"/>`;
}).join('');
const FAVICON = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><circle cx="100" cy="100" r="97" fill="#121821" stroke="#E9C77B" stroke-width="6"/><g stroke="#E9C77B" stroke-width="3" stroke-linecap="round" opacity="0.4">${RAYS}</g><text x="100" y="131" text-anchor="middle" font-family="Instrument Serif, Georgia, serif" font-size="104" fill="#F1EEE8">A<tspan font-style="italic" font-size="70" fill="#E9C77B" dx="2">t</tspan></text></svg>`;

// Cloudflare Web Analytics (free, cookieless). The token is public by design.
const CF_ANALYTICS = `<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "f15c7169aefc45a6abc5c632e642ae7b"}'></script><!-- End Cloudflare Web Analytics -->`;

function page({ title, body, description = HEADLINE, accent = '#E9C77B', noindex = false, showHeadline = true }) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description)}">
${noindex ? '<meta name="robots" content="noindex">\n' : ''}<link rel="icon" href="${BASE}/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{--night:#0B0F14;--panel:#121821;--line:#222B38;--ivory:#F1EEE8;--mist:#C4C9D2;--slate:#8A93A3;--gold:#E9C77B;--accent:${accent}}
*{box-sizing:border-box}
html,body{margin:0;background:var(--night);color:var(--ivory);font:400 18px/1.6 Inter,system-ui,sans-serif}
a{color:var(--gold)}
.wrap{max-width:720px;margin:0 auto;padding:32px 24px 64px}
header{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid var(--line);padding-bottom:16px}
.mark{display:inline-flex;align-items:center;gap:12px;font:400 30px/1 'Instrument Serif',Georgia,serif;color:var(--ivory);text-decoration:none}
.mark .sun{width:60px;height:auto;flex:none}
.mark em{color:var(--gold)}
.stamp{font:500 13px/1 Inter,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
h1{font:400 clamp(40px,8vw,64px)/1.05 'Instrument Serif',Georgia,serif;margin:40px 0 16px}
h1 em{color:var(--accent)}
.dateline{color:var(--mist);font-size:16px;border-left:3px solid var(--accent);padding-left:12px}
.headline{color:var(--mist);font-size:16px;margin-top:8px}
footer{margin-top:64px;border-top:1px solid var(--line);padding-top:16px;color:var(--slate);font-size:14px}
</style>
${CF_ANALYTICS}
</head>
<body><div class="wrap">
<header><a class="mark" href="${BASE}/" aria-label="Awestruck Today home">${MARK}<span>Awestruck <em>Today</em></span></a></header>
${showHeadline ? `<p class="headline">${esc(HEADLINE)}</p>` : ''}
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
    : `<h1>Launching <em>Nov 28</em></h1>
<p>One true story every day of what God did through one ordinary, flawed person, with every date, quote and number sourced.</p>`;
  await writeFile(join(OUT, 'index.html'), page({ title: 'Awestruck Today', body: home, showHeadline: !!latest }));
  await writeFile(join(OUT, '404.html'), page({ title: 'Not found — Awestruck Today', body: `<h1>Page not found</h1><p><a href="${BASE}/today/">Go to today's story</a></p>`, noindex: true }));
  await writeFile(join(OUT, '.nojekyll'), '');
  await writeFile(join(OUT, 'favicon.svg'), FAVICON);

  console.log(`Built ${live.length} of ${all.length} entries for ${TODAY} (Eastern) into ${OUT}/`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(err => { console.error(err.message); process.exit(1); });
}
