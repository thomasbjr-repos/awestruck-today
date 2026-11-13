// Entries, the midnight-Eastern release rule, and the weekly themes.
// Plain Node (no Astro imports), so scripts/test-build.mjs can test it directly.
//
// Env (all optional):
//   AT_TODAY    YYYY-MM-DD   pretend "today" (tests and previews)
//   AT_CONTENT  folder       where entry JSON files live (default content/entries)

import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

export const TZ = 'America/New_York';

export function todayInEastern(now = new Date()) {
  // en-CA formats as YYYY-MM-DD
  return new Intl.DateTimeFormat('en-CA', { timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit' }).format(now);
}

export function today() {
  return process.env.AT_TODAY || todayInEastern();
}

// Statuses set from the Entry Database. Only these ever reach the website.
export const APPROVED = new Set(['Verified', 'Produced', 'Scheduled', 'Published']);

export function publishable(entries, day) {
  return entries
    .filter(e => APPROVED.has(e.status) && e.date <= day)
    .sort((a, b) => a.date.localeCompare(b.date));
}

// The weekly rotation (Concept Brief). Keys match data-day in site.css and the theme icons.
export const DAYS = [
  { key: 'sun', dow: 'Sunday', theme: 'Preachers & Sermons', short: 'Preachers', blurb: 'Preachers, the sermons that stopped people in their tracks, and the revivals that followed' },
  { key: 'mon', dow: 'Monday', theme: 'Missions & Movements', short: 'Missions', blurb: 'Missionaries, people who founded works of mercy, and the ones who started movements of prayer' },
  { key: 'tue', dow: 'Tuesday', theme: 'Books & Writings', short: 'Books', blurb: 'Theologians, novelists, apologists and letter-writers whose words still travel' },
  { key: 'wed', dow: 'Wednesday', theme: 'Music & Hymns', short: 'Music', blurb: 'Hymn writers, composers and worship artists, and the songs they first gave the church' },
  { key: 'thu', dow: 'Thursday', theme: 'Arts & Film', short: 'Arts & Film', blurb: 'Painters, sculptors, illustrators, photographers and filmmakers' },
  { key: 'fri', dow: 'Friday', theme: 'Science, Education & Thinkers', short: 'Science', blurb: 'Scientists, university founders and philosophers who studied the world God made' },
  { key: 'sat', dow: 'Saturday', theme: 'Entrepreneurs & Builders', short: 'Builders', blurb: 'Business founders, philanthropists and workplace innovators who built with faith' },
];
export const THEME_KEY = Object.fromEntries(DAYS.map(d => [d.theme, d.key]));

const REQUIRED = ['date', 'slug', 'title', 'person', 'theme', 'status'];

export function loadEntries(dir = process.env.AT_CONTENT || 'content/entries') {
  let files = [];
  try { files = readdirSync(dir).filter(f => f.endsWith('.json')); } catch { return []; }
  return files.map(f => {
    const e = JSON.parse(readFileSync(join(dir, f), 'utf8'));
    for (const k of REQUIRED) if (!e[k]) throw new Error(`${f}: missing "${k}"`);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(e.date)) throw new Error(`${f}: date must be YYYY-MM-DD`);
    if (!/^[a-z0-9-]+$/.test(e.slug)) throw new Error(`${f}: slug must be lowercase letters, digits, hyphens`);
    if (!THEME_KEY[e.theme]) throw new Error(`${f}: unknown theme "${e.theme}"`);
    return e;
  });
}

let cache;
export function liveEntries() {
  if (!cache) cache = publishable(loadEntries(), today());
  return cache;
}

// ---------- Small helpers ----------
export const entryPath = e => `/${e.date.slice(5)}/${e.slug}/`;
const asDate = d => new Date(d + 'T12:00:00Z');
export const weekdayKey = d => DAYS[asDate(d).getUTCDay()].key;
export const dayInfo = d => DAYS[asDate(d).getUTCDay()];
export const longDate = d => asDate(d).toLocaleDateString('en-US', { timeZone: 'UTC', month: 'long', day: 'numeric', year: 'numeric' });
export const shortStamp = d => asDate(d).toLocaleDateString('en-US', { timeZone: 'UTC', month: 'short', day: 'numeric' }).toUpperCase();
export function addDays(d, n) { const x = asDate(d); x.setUTCDate(x.getUTCDate() + n); return x.toISOString().slice(0, 10); }
export const yearsAgo = (eventYear, d) => Number(d.slice(0, 4)) - Number(eventYear);

// Text with *italics* → safe HTML (everything else escaped).
export const esc = (s = '') => String(s)
  .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;').replaceAll("'", '&#39;');
export const inline = (s = '') => esc(s).replace(/\*(.+?)\*/g, '<i>$1</i>');

// Month grids for the Archive: newest month first, Sunday-first weeks.
export function monthsBetween(first, last) {
  const out = [];
  let y = Number(first.slice(0, 4)), m = Number(first.slice(5, 7));
  const ly = Number(last.slice(0, 4)), lm = Number(last.slice(5, 7));
  while (y < ly || (y === ly && m <= lm)) {
    out.push(`${y}-${String(m).padStart(2, '0')}`);
    m++; if (m > 12) { m = 1; y++; }
  }
  return out.reverse();
}
export function monthCells(ym) {
  const [y, m] = ym.split('-').map(Number);
  const first = new Date(Date.UTC(y, m - 1, 1, 12));
  const days = new Date(Date.UTC(y, m, 0, 12)).getUTCDate();
  const cells = Array.from({ length: first.getUTCDay() }, () => null);
  for (let n = 1; n <= days; n++) cells.push(`${ym}-${String(n).padStart(2, '0')}`);
  return cells;
}
export const monthLabel = ym => asDate(ym + '-01').toLocaleDateString('en-US', { timeZone: 'UTC', month: 'long', year: 'numeric' });
