import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");

const read = (path) => readFileSync(resolve(root, path), "utf8");

const skill = read("SKILL.md");
const readme = read("README.md");
const spec = read("docs/sdlc-autopilot-spec.html");
const workflow = read(".github/workflows/validate.yml");
const gitignore = read(".gitignore");

const bundledPathMatches = [
  ...skill.matchAll(/`((?:references|scripts)\/[A-Za-z0-9._/-]+)/g),
];
const bundledPaths = [...new Set(bundledPathMatches.map((match) => match[1]))];

assert(bundledPaths.length > 0, "SKILL.md should reference bundled resource paths");

for (const path of bundledPaths) {
  assert(existsSync(resolve(root, path)), `SKILL.md references missing bundled resource: ${path}`);
}

const minimumRuntimeFiles = [
  "SKILL.md",
  "references/self-verification.md",
  "references/deep-audit.md",
  "references/deployment.md",
  "scripts/verify-pipeline.sh",
  "scripts/verify-inversion.sh",
];

for (const path of minimumRuntimeFiles) {
  assert(existsSync(resolve(root, path)), `missing minimum runtime file: ${path}`);
  assert(readme.includes(path), `README should list minimum runtime file: ${path}`);
}

assert(
  readme.includes("copy the entire `sdlc-autopilot/` skill folder"),
  "README should instruct manual installers to copy the whole skill folder",
);
assert(
  readme.includes("Do not copy `SKILL.md` by itself"),
  "README should explicitly reject SKILL.md-only installs",
);
assert(
  !readme.includes("copy the `SKILL.md` file"),
  "README must not recommend copying only SKILL.md",
);
assert(
  spec.includes("SKILL.md</code>-only install is incomplete"),
  "browser spec should document that SKILL.md-only installs are incomplete",
);
assert(
  skill.includes("Install this as the complete `sdlc-autopilot/` skill package"),
  "SKILL.md should state the complete-package install requirement",
);

const forbiddenReleaseFiles = ["SKILL-rewrite-proposal.md"];

for (const path of forbiddenReleaseFiles) {
  assert(!existsSync(resolve(root, path)), `release package should not include stale internal file: ${path}`);
}

const requiredCiCommands = [
  "node --test scripts/verify-pipeline.test.mjs docs/sdlc-autopilot-spec.test.mjs scripts/skill-package.test.mjs",
  "sh -n scripts/verify-pipeline.sh",
  "sh -n scripts/verify-inversion.sh",
  "python3 -m py_compile scripts/run-agent-evals.py",
];

for (const command of requiredCiCommands) {
  assert(workflow.includes(command), `CI should run release guard: ${command}`);
}

for (const pattern of ["__pycache__/", "*.pyc"]) {
  assert(gitignore.includes(pattern), `.gitignore should exclude Python bytecode pattern: ${pattern}`);
}

process.stdout.write("skill package validation passed\n");
