import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const html = readFileSync(resolve(here, "sdlc-autopilot-spec.html"), "utf8");

const requiredTabs = [
  'data-tab="quick"',
  'data-tab="standard"',
  'data-tab="full"',
  'data-tab="expert"',
];

for (const tab of requiredTabs) {
  assert(html.includes(tab), `missing mode tab: ${tab}`);
}

const requiredSources = [
  "../SKILL.md",
  "../README.md",
  "../GUIDANCE.md",
  "../references/self-verification.md",
  "../references/deep-audit.md",
  "../references/deployment.md",
  "../scripts/verify-pipeline.sh",
  "../scripts/verify-pipeline.test.mjs",
  "../evals/evals.json",
  "../evals/agent-run.schema.json",
  "../evals/empirical-results.md",
  "../SECURITY.md",
  "../CHANGELOG.md",
];

for (const source of requiredSources) {
  assert(html.includes(source), `missing source reference: ${source}`);
}

const svgCount = (html.match(/<svg\b/g) || []).length;
assert(svgCount >= 6, "expected at least six inline SVG diagrams or pictures");

const requiredCopy = [
  "Fix-Guard-Test-Verify",
  "Standard is 5 phases",
  "HUMAN REVIEW RECOMMENDED: This change touches [domain].",
  "AI-assisted review",
  "Ready Gate",
  "Strict inversion",
  "Trust Model",
  "untracked files",
  "ASVS 5.0.0",
  "NIST SSDF",
];

for (const phrase of requiredCopy) {
  assert(html.includes(phrase), `missing required copy: ${phrase}`);
}

assert(!/https?:\/\//.test(html), "spec should not depend on external URLs or assets");
assert(/addEventListener\("click"/.test(html), "tab click behavior should be wired");
assert(/addEventListener\("keydown"/.test(html), "keyboard tab behavior should be wired");

process.stdout.write("sdlc-autopilot-spec.html validation passed\n");
