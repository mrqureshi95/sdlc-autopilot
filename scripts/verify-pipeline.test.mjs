import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { chmodSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, "..");
const verifier = resolve(repoRoot, "skills", "sdlc-autopilot", "scripts", "verify-pipeline.sh");

function run(command, args, cwd, options = {}) {
  return execFileSync(command, args, {
    cwd,
    encoding: "utf8",
    env: { ...process.env, ...options.env },
    stdio: ["ignore", "pipe", "pipe"],
  });
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

test("verify-pipeline counts node assert method calls in changed tests", () => {
  const workdir = mkdtempSync(join(tmpdir(), "sdlc-verify-assert-methods-"));
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
      join(workdir, "method-assertions.test.mjs"),
      [
        'import assert from "node:assert/strict";',
        "assert.equal(2 + 2, 4);",
        "assert.deepEqual(['guard'], ['guard']);",
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

test("verify-pipeline finds bundled verify-inversion when run from an installed skill path", () => {
  const workdir = mkdtempSync(join(tmpdir(), "sdlc-verify-installed-skill-"));
  const skillDir = mkdtempSync(join(tmpdir(), "sdlc-installed-skill-"));
  try {
    mkdirSync(join(skillDir, "scripts"));
    writeFileSync(join(skillDir, "scripts", "verify-pipeline.sh"), run("cat", [verifier], repoRoot));
    writeFileSync(
      join(skillDir, "scripts", "verify-inversion.sh"),
      run("cat", [resolve(repoRoot, "skills", "sdlc-autopilot", "scripts", "verify-inversion.sh")], repoRoot),
    );

    mkdirSync(join(workdir, "bin"));
    mkdirSync(join(workdir, "src"));
    writeFileSync(
      join(workdir, "bin", "npx"),
      "#!/bin/sh\nif grep -q fixed src/message.js; then exit 0; fi\nprintf 'behavior mismatch\\n' >&2\nexit 1\n",
    );
    chmodSync(join(workdir, "bin", "npx"), 0o755);
    writeFileSync(join(workdir, "jest.config.js"), "export default {};\n");
    writeFileSync(join(workdir, "src", "message.js"), "export function message() { return 'old'; }\n");
    writeFileSync(
      join(workdir, "src", "message.test.js"),
      [
        'import assert from "node:assert/strict";',
        'import { message } from "./message.js";',
        "assert.equal(message(), 'old');",
        "",
      ].join("\n"),
    );

    run("git", ["init", "-q"], workdir);
    run("git", ["config", "user.email", "test@sdlc-autopilot.local"], workdir);
    run("git", ["config", "user.name", "SDLC Test"], workdir);
    run("git", ["add", "."], workdir);
    run("git", ["commit", "-q", "-m", "base"], workdir);

    writeFileSync(join(workdir, "src", "message.js"), "export function message() { return 'fixed'; }\n");
    writeFileSync(
      join(workdir, "src", "message.test.js"),
      [
        'import assert from "node:assert/strict";',
        'import { message } from "./message.js";',
        "assert.equal(message(), 'fixed');",
        "assert.notEqual(message(), 'old');",
        "",
      ].join("\n"),
    );

    const output = run("sh", [join(skillDir, "scripts", "verify-pipeline.sh"), "standard"], workdir, {
      env: {
        PATH: `${join(workdir, "bin")}:${process.env.PATH}`,
        SDLC_STRICT_INVERSION: "1",
      },
    });
    assert(/Strict inversion verification passed/.test(output), output);
  } finally {
    rmSync(workdir, { recursive: true, force: true });
    rmSync(skillDir, { recursive: true, force: true });
  }
});

test("verify-pipeline reports skipped bundled inversion as skipped, not passed", () => {
  const workdir = mkdtempSync(join(tmpdir(), "sdlc-verify-inversion-skip-"));
  const skillDir = mkdtempSync(join(tmpdir(), "sdlc-installed-skill-skip-"));
  try {
    mkdirSync(join(skillDir, "scripts"));
    writeFileSync(join(skillDir, "scripts", "verify-pipeline.sh"), run("cat", [verifier], repoRoot));
    writeFileSync(
      join(skillDir, "scripts", "verify-inversion.sh"),
      run("cat", [resolve(repoRoot, "skills", "sdlc-autopilot", "scripts", "verify-inversion.sh")], repoRoot),
    );
    writeFileSync(join(workdir, "value.mjs"), "export const value = 'old';\n");
    writeFileSync(
      join(workdir, "value.test.mjs"),
      [
        'import assert from "node:assert/strict";',
        'import { value } from "./value.mjs";',
        "assert.equal(value, 'old');",
        "assert.notEqual(value, 'fixed');",
        "",
      ].join("\n"),
    );

    run("git", ["init", "-q"], workdir);
    run("git", ["config", "user.email", "test@sdlc-autopilot.local"], workdir);
    run("git", ["config", "user.name", "SDLC Test"], workdir);
    run("git", ["add", "."], workdir);
    run("git", ["commit", "-q", "-m", "base"], workdir);

    writeFileSync(join(workdir, "value.mjs"), "export const value = 'fixed';\n");
    writeFileSync(
      join(workdir, "value.test.mjs"),
      [
        'import assert from "node:assert/strict";',
        'import { value } from "./value.mjs";',
        "assert.equal(value, 'fixed');",
        "assert.notEqual(value, 'old');",
        "",
      ].join("\n"),
    );

    const output = run("sh", [join(skillDir, "scripts", "verify-pipeline.sh"), "standard"], workdir, {
      env: { SDLC_STRICT_INVERSION: "1" },
    });
    assert(!/Strict inversion verification passed/.test(output), output);
    assert(/Strict inversion verification skipped/.test(output), output);
    assert(/No supported targeted test runner detected/.test(output), output);
  } finally {
    rmSync(workdir, { recursive: true, force: true });
    rmSync(skillDir, { recursive: true, force: true });
  }
});
