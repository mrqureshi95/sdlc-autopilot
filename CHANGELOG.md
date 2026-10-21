# Changelog

## [Unreleased]

## [2.0.0] - 2026-10-21

### Breaking changes
- Helper exits now mean scoped checks satisfied (0), observed failure (1), or missing required evidence (2). Zero/opaque tests and unsupported automatic inversion no longer imply success. Review is separate from implementation; installed commands resolve from the complete skill folder.

### Added
- Optional local real-task record template and a paired evaluation protocol for measuring task acceptance, defects, human rework, time and workflow friction. No usage telemetry or model campaign is enabled.

### Changed
- Public-release readiness: provider-neutral host guidance, bundled MIT notice, real three-host installer smoke, fresh Jest/Vitest/JUnit evidence adapters, and maintained checksum-pinned Gitleaks controls/CI. Fix negative JUnit counter cancellation; remove the vulnerable test-only sprintf-js chain with a scoped YAML override and compatibility control.
- Follow-up re-audit: preserve final-state provenance across commands, require evidence per selected project, honor explicit empty configuration, handle Node TODO outcomes, detect index-flag-hidden edits without changing user flags, and align contributor/security/scenario guidance.
- Add reproducible controlled verifier comparisons and a responsive, single-page printable HTML field guide.
- Separate read-only review from implementation and risk selection; preserve authorization and user work without routine pauses or automatic cleanup.
- Replace heuristic Ready Gate guarantees with scoped pass/fail/inconclusive/not-applicable evidence, exact Git provenance and optional task-start snapshots.
- Combine branch/worktree/untracked changes with NUL-safe paths; report mixed ownership and scan exclusions honestly.
- Remove assertion-count, stale-coverage and automatic-inversion guarantees; require positive supported test execution for behavioral evidence.
- Run inspected explicit project checks with POSIX timeouts, no implicit downloads, and opt-in scoped fixes.
- Replace unsafe security/deployment recipes with context-aware framework controls and platform-specific preparation/recovery guidance.
- Make external-provider review opt-in, scoped and redacted; treat diffs/tool output as untrusted data.
- Separate structural evaluation, semantic replay, text checks and human judgments. Pin the evaluation runtime, add adversarial regressions and evaluator-owned semantic oracles, and retain human criteria as pending.
- Align README, guidance, browser overview, examples and evaluation prompts with the narrowed evidence contract. No agent pass-rate or performance claims.

Earlier release notes below describe historical behavior, not current guarantees.

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

[Unreleased]: https://github.com/mrqureshi95/sdlc-autopilot/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/mrqureshi95/sdlc-autopilot/releases/tag/v2.0.0
[1.0.0]: https://github.com/mrqureshi95/sdlc-autopilot/releases/tag/v1.0.0
