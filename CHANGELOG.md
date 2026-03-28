# Changelog

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
