// Checks the midnight-Eastern release rule without touching real content.
// Run: node scripts/test-build.mjs
import { strict as assert } from 'node:assert';
import { mkdtemp, mkdir, writeFile, readFile, access } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { todayInEastern, publishable } from './build.mjs';

// Eastern date rollover: 04:59 UTC on Dec 13 (EST) is still Dec 12 in New York; 05:00 is Dec 13.
assert.equal(todayInEastern(new Date('2026-12-13T04:59:00Z')), '2026-12-12');
assert.equal(todayInEastern(new Date('2026-12-13T05:00:00Z')), '2026-12-13');
// Daylight time: midnight Eastern is 04:00 UTC in summer.
assert.equal(todayInEastern(new Date('2027-07-04T03:59:00Z')), '2027-07-03');
assert.equal(todayInEastern(new Date('2027-07-04T04:00:00Z')), '2027-07-04');

const base = { person: 'Test Person', theme: 'Arts & Film', title: 'T' };
const list = [
  { ...base, date: '2026-12-12', slug: 'a', status: 'Verified' },
  { ...base, date: '2026-12-13', slug: 'b', status: 'Produced' },
  { ...base, date: '2026-12-14', slug: 'c', status: 'Produced' }, // future
  { ...base, date: '2026-12-10', slug: 'd', status: 'Draft' },    // never published
];
assert.deepEqual(publishable(list, '2026-12-13').map(e => e.slug), ['a', 'b']);

// End to end: a future page must not exist in the build output.
const dir = await mkdtemp(join(tmpdir(), 'awe-'));
const content = join(dir, 'content'); const out = join(dir, 'site');
await mkdir(content);
for (const e of list) await writeFile(join(content, `${e.slug}.json`), JSON.stringify(e));
execFileSync('node', ['scripts/build.mjs', '--today', '2026-12-13', '--content', content, '--out', out]);
await access(join(out, '12-13/b/index.html'));
await assert.rejects(access(join(out, '12-14/c/index.html')));
await assert.rejects(access(join(out, '12-10/d/index.html')));
const today = await readFile(join(out, 'today/index.html'), 'utf8');
assert.ok(today.includes('/12-13/b/'), '/today points at today\'s entry');

console.log('All release-rule checks passed.');
