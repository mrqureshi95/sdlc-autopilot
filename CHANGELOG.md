# Changelog

## [Unreleased]

### Changed
- Standard mode is now a 5-phase workflow: Understand, Implement, Verify, Ready Gate, Ship.
- The old split between gate/test, audit, and regression/final verification was collapsed into a single Verify phase.
- LOG and ANNOUNCE ceremony was removed from the live workflow and from the primary documentation examples.
- Quick mode is now described as a trivial-path flow with immediate promotion to Standard when behavior changes, tests, or guardrails are required.
- Ready Gate language now centers on evidence: raw verifier output, critical outcomes, contradiction handling, honest limitations, and optional second-model review.
- Expert mode is now explicit: it removes presentation overhead without weakening TDD bias, guardrails, edge-case closure, SSOT, DRY-with-judgment, or verification.
- The self-verification reference was reduced to 10 critical outcomes.
- The external verifier was hardened with coverage-artifact checks when available, executable guardrail signals, stronger assertion-count checks in changed tests, and the existing safety scans.
- Eval language and walkthroughs were rewritten to focus on outcomes instead of process theater.

### Added
- Outcome-focused machine-check support in [scripts/run-agent-evals.py](/Users/muhammadqureshi/Projects/sdlc-autopilot/scripts/run-agent-evals.py): `diff_not_contains`, `verify_output_contains`, `transcript_not_contains`, and `file_contains`.
- Explicit expert-mode coverage in the eval suite.
- Long-form guidance aligned with the live skill in [GUIDANCE.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/GUIDANCE.md).
- Updated walkthroughs aligned with the current workflow in [examples/quick-change-walkthrough.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/examples/quick-change-walkthrough.md), [examples/bug-fix-walkthrough.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/examples/bug-fix-walkthrough.md), and [examples/feature-walkthrough.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/examples/feature-walkthrough.md).

## [1.0.0] - 2026-03-26

### Added
- Core SKILL.md with quick/standard/full mode pipelines
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
