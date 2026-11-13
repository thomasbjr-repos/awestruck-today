// Checks the midnight-Eastern release rule, then builds the real site with test entries
// and confirms future and unapproved pages don't exist. The deploy stops if this fails.
// Run: npm test   (needs `npm install` first)
import { strict as assert } from 'node:assert';
import { mkdtemp, mkdir, writeFile, readFile, access } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { todayInEastern, publishable, monthCells, weekdayKey } from '../src/lib/entries.mjs';

// Eastern date rollover: 04:59 UTC on Dec 13 (EST) is still Dec 12 in New York; 05:00 is Dec 13.
assert.equal(todayInEastern(new Date('2026-12-13T04:59:00Z')), '2026-12-12');
assert.equal(todayInEastern(new Date('2026-12-13T05:00:00Z')), '2026-12-13');
// Daylight time: midnight Eastern is 04:00 UTC in summer.
assert.equal(todayInEastern(new Date('2027-07-04T03:59:00Z')), '2027-07-03');
assert.equal(todayInEastern(new Date('2027-07-04T04:00:00Z')), '2027-07-04');

// Calendar helpers: Dec 1, 2026 is a Tuesday; Nov 13, 2026 a Friday.
assert.equal(monthCells('2026-12').indexOf('2026-12-01'), 2);
assert.equal(weekdayKey('2026-11-13'), 'fri');

const base = { person: 'Test Person', theme: 'Arts & Film', title: 'Test entry' };
const list = [
  { ...base, date: '2026-12-12', slug: 'a', status: 'Verified', theme: 'Entrepreneurs & Builders' },
  { ...base, date: '2026-12-13', slug: 'b', status: 'Produced', theme: 'Preachers & Sermons', hook: 'A *test* hook', numbers: [{ value: '93', meaning: 'test figures', tier: 'B' }] },
  { ...base, date: '2026-12-14', slug: 'c', status: 'Produced' }, // future
  { ...base, date: '2026-12-10', slug: 'd', status: 'Draft' },    // never published
];
assert.deepEqual(publishable(list, '2026-12-13').map(e => e.slug), ['a', 'b']);

// End to end: build the real Astro site with these entries, "today" = Dec 13.
const dir = await mkdtemp(join(tmpdir(), 'awe-'));
const content = join(dir, 'content'); const out = join(dir, 'site');
await mkdir(content);
for (const e of list) await writeFile(join(content, `${e.slug}.json`), JSON.stringify(e));
execFileSync('npx', ['astro', 'build'], {
  stdio: 'inherit',
  env: { ...process.env, AT_TODAY: '2026-12-13', AT_CONTENT: content, AT_OUT: out, BASE_PATH: '' },
});
await access(join(out, '12-13/b/index.html'));
await access(join(out, '12-12/a/index.html'));
await assert.rejects(access(join(out, '12-14/c/index.html')), 'future entry must not be built');
await assert.rejects(access(join(out, '12-10/d/index.html')), 'draft entry must not be built');
const today = await readFile(join(out, 'today/index.html'), 'utf8');
assert.ok(today.includes('/12-13/b/'), '/today points at today\'s entry');
const entry = await readFile(join(out, '12-13/b/index.html'), 'utf8');
assert.ok(entry.includes('<i>test</i>'), 'hook italics render');
assert.ok(entry.includes('data-day="sun"'), 'theme color set from the theme');
const archive = await readFile(join(out, 'archive/index.html'), 'utf8');
assert.ok(archive.includes('/12-12/a/') && !archive.includes('/12-14/c/'), 'archive lists only live entries');
await access(join(out, 'about/index.html'));
await access(join(out, 'what-we-believe/index.html'));
await access(join(out, '404.html'));

console.log('All release-rule and build checks passed.');
