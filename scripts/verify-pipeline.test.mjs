import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
test('installed absolute entrypoint reports missing provenance without a false pass', () => {
  const dir = mkdtempSync(join(tmpdir(), 'sdlc-installed-'));
  try {
    let error;
    try { execFileSync('sh', [join(root,'skills/sdlc-autopilot/scripts/verify-pipeline.sh'),'full','--json'], { cwd:dir, encoding:'utf8' }); }
    catch(e) { error=e; }
    assert.equal(error?.status, 2);
    assert.equal(JSON.parse(error.stdout).status, 'inconclusive');
  } finally { rmSync(dir,{recursive:true,force:true}); }
});
