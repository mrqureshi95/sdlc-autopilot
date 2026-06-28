# Changelog

## [Unreleased]

### Changed
- Standard mode is now a 5-phase workflow: Understand, Implement, Verify, Ready Gate, Ship.
- The old split between gate/test, audit, and regression/final verification was collapsed into a single Verify phase.
- LOG and ANNOUNCE ceremony was removed from the live workflow and from the primary documentation examples.
- Quick mode is now described as a trivial-path flow with immediate promotion to Standard when behavior changes, tests, or guardrails are required.
- Ready Gate language now centers on evidence: raw verifier output, critical outcomes, contradiction handling, honest limitations, and optional second-model review.
- Expert mode is now explicit: it removes presentation overhead without weakening TDD bias, guardrails, edge-case closure, SSOT, DRY-with-judgment, or verification.
- The self-verification reference was reduced to 10 critical outcomes and now states the Ready Gate trust boundary.
- The external verifier was hardened with untracked-file detection, coverage-artifact checks when available, executable guardrail signals, stronger assertion-count checks in changed tests, and the existing safety scans.
- The external verifier now runs changed Node `.test.mjs` / `.test.js` files with `node --test` when a project has no package-level test runner.
- CI validation now runs the package/spec/verifier Node tests, all release shell script syntax checks, and Python syntax checks for the agent eval harness.
- Eval language and walkthroughs were rewritten to focus on outcomes instead of process theater.
- Full-mode deep audit guidance now maps high-risk review work to OWASP ASVS 5.0.0 areas and NIST SSDF practice groups without claiming formal compliance.
- Installation guidance now requires the complete `sdlc-autopilot/` skill package instead of a `SKILL.md`-only copy.
- The installable skill now lives under `skills/sdlc-autopilot/` so GitHub installs copy `SKILL.md`, `references/`, and runtime `scripts/` as one package.
- The external verifier now counts Node `assert.equal(...)` / `assert.deepEqual(...)`-style test assertions as guardrail and assertion-count evidence.
- Strict inversion verification now resolves the bundled `verify-inversion.sh` from the installed skill package and reports unsupported runner results as skipped rather than passed.
- The release package no longer includes the obsolete `SKILL-rewrite-proposal.md` draft.
- The browser specification now reflects the public release path and derives its `SKILL.md` line-count check from the live file.

### Added
- Outcome-focused machine-check support in [scripts/run-agent-evals.py](scripts/run-agent-evals.py): `diff_not_contains`, `verify_output_contains`, `transcript_not_contains`, and `file_contains`.
- Explicit expert-mode coverage in the eval suite.
- Long-form guidance aligned with the live skill in [GUIDANCE.md](GUIDANCE.md).
- Updated walkthroughs aligned with the current workflow in [examples/quick-change-walkthrough.md](examples/quick-change-walkthrough.md), [examples/bug-fix-walkthrough.md](examples/bug-fix-walkthrough.md), and [examples/feature-walkthrough.md](examples/feature-walkthrough.md).
- Trust-model and non-use guidance in the live skill and public documentation.
- Regression test for verifier handling of brand-new untracked files in [scripts/verify-pipeline.test.mjs](scripts/verify-pipeline.test.mjs).
- Regression tests for Node `assert.*(...)` assertion counting, installed-skill strict inversion path resolution, and honest strict inversion skip reporting in [scripts/verify-pipeline.test.mjs](scripts/verify-pipeline.test.mjs).
- Regression test for complete skill-package installation guidance and bundled resource references in [scripts/skill-package.test.mjs](scripts/skill-package.test.mjs).
- Honest empirical evidence page and multi-agent reporting rules in [evals/empirical-results.md](evals/empirical-results.md).
- Optional agent metadata fields in [evals/agent-run.schema.json](evals/agent-run.schema.json) for reproducible multi-agent eval campaigns.

## [1.0.0] - 2026-03-26

### Added
- Core `SKILL.md` with quick/standard/full mode pipelines
- Fix-Guard-Test-Verify loop — the core innovation
- Mode selection logic (risk classification + user language signals)
- 7-phase standard pipeline with 2-pass audit
- Full mode additions: convergence pass, security deep dive, user checkpoint
- `references/deep-audit.md` — security checklist, guardrail pattern library, API contract validation, migration guidance
- `references/deployment.md` — Supabase, Vercel, Netlify, AWS, Docker, generic git
- `scripts/detect-toolchain.sh` — auto-detect project toolchain
- `scripts/run-gates.sh` — lint, format, typecheck, test runner
- 10 eval test cases covering all modes, circuit breaker, root cause scanning, audit-finding guarding
- Project fixtures for each eval test case
- Example walkthroughs for quick, bug-fix, and feature modes
- Dynamic skill delegation
- Graceful degradation for missing tooling
- Circuit breaker for fix-induced regressions
- Guardrail completeness check in Phase 5
- Proportionality rules (structural/behavioral/cosmetic)

[Unreleased]: https://github.com/mrqureshi95/sdlc-autopilot/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/mrqureshi95/sdlc-autopilot/releases/tag/v1.0.0
