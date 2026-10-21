import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { dirname, resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const skillRoot=join(root,'skills/sdlc-autopilot');
test('installable package is complete and linked bundled resources exist', () => {
  assert(!existsSync(join(root,'SKILL.md')));
  const skill=readFileSync(join(skillRoot,'SKILL.md'),'utf8');
  assert.match(skill,/^---\nname: sdlc-autopilot\ndescription: .+\nlicense: MIT\nmetadata:\n  version: "2\.0\.0"\n  compatibility: [^\n]{1,500}\n---/);
  for (const match of skill.matchAll(/`((?:scripts|references)\/[\w./-]+)\b/g)) {
    assert(existsSync(join(skillRoot,match[1])),match[1]);
  }
  assert.equal(readFileSync(join(skillRoot,'LICENSE.txt'),'utf8'),readFileSync(join(root,'LICENSE.txt'),'utf8'));
  const scripts=readdirSync(join(skillRoot,'scripts'));
  for (const file of ['evidence.py','node-test-reporter.mjs','detect-toolchain.sh','run-gates.sh','verify-pipeline.sh','verify-inversion.sh']) assert(scripts.includes(file),file);
  assert(skill.split('\n').length<230,'keep the entrypoint lean');
});
