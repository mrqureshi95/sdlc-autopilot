import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
test('browser overview links to canonical existing local sources', () => {
  const html=readFileSync(resolve(here,'sdlc-autopilot-spec.html'),'utf8');
  assert.match(html,/<html lang="en">/);
  assert.match(html,/<meta name="viewport"/);
  for (const m of html.matchAll(/href="([^"]+)"/g)) assert(existsSync(resolve(here,m[1])),m[1]);
  assert(!/<script\b|https?:\/\//.test(html),'static overview has no remote dependencies or executable scripts');
});
