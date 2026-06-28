import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, "..");
const verifier = resolve(repoRoot, "scripts", "verify-pipeline.sh");

function run(command, args, cwd) {
  return execFileSync(command, args, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
}

test("verify-pipeline includes untracked files in change evidence", () => {
  const workdir = mkdtempSync(join(tmpdir(), "sdlc-verify-"));
  try {
    mkdirSync(join(workdir, "scripts"));
    writeFileSync(join(workdir, "scripts", "verify-pipeline.sh"), run("cat", [verifier], repoRoot));
    writeFileSync(join(workdir, "README.md"), "# fixture\n");

    run("git", ["init", "-q"], workdir);
    run("git", ["config", "user.email", "test@sdlc-autopilot.local"], workdir);
    run("git", ["config", "user.name", "SDLC Test"], workdir);
    run("git", ["add", "."], workdir);
    run("git", ["commit", "-q", "-m", "base"], workdir);

    writeFileSync(join(workdir, "new-feature.js"), "export function answer() { return 42; }\n");

    const output = run("sh", ["scripts/verify-pipeline.sh", "quick"], workdir);
    assert(/Changes detected: .*including 1 untracked file/.test(output), output);
    assert(/No hardcoded secrets detected/.test(output), output);
  } finally {
    rmSync(workdir, { recursive: true, force: true });
  }
});

test("verify-pipeline runs changed Node test files when no package runner exists", () => {
  const workdir = mkdtempSync(join(tmpdir(), "sdlc-verify-node-"));
  try {
    mkdirSync(join(workdir, "scripts"));
    writeFileSync(join(workdir, "scripts", "verify-pipeline.sh"), run("cat", [verifier], repoRoot));
    writeFileSync(join(workdir, "README.md"), "# fixture\n");

    run("git", ["init", "-q"], workdir);
    run("git", ["config", "user.email", "test@sdlc-autopilot.local"], workdir);
    run("git", ["config", "user.name", "SDLC Test"], workdir);
    run("git", ["add", "."], workdir);
    run("git", ["commit", "-q", "-m", "base"], workdir);

    writeFileSync(
      join(workdir, "example.test.mjs"),
      [
        'import assert from "node:assert/strict";',
        "assert(2 + 2 === 4);",
        "assert(/guard/.test('guardrail'));",
        "",
      ].join("\n"),
    );

    const output = run("sh", ["scripts/verify-pipeline.sh", "standard"], workdir);
    assert(/Tests pass/.test(output), output);
    assert(/Assertion-count signal: 2 assertions across 1 test file/.test(output), output);
  } finally {
    rmSync(workdir, { recursive: true, force: true });
  }
});
