# Changelog

## [Unreleased]

### Changed
- Token budgets clarified as "skill instruction overhead only" — excludes user code reading and tool calls
- Branch behavior: warn before committing to main/master instead of forcing branch creation; user can say "commit to main" to override
- Phase 4 audit reframed as explicit checklists (correctness + security) instead of open-ended review
- Convergence shortcut: pass 1 no longer gates pass 2 thoroughness — correctness and security are independent concerns
- Phase 3/4 scope clarified: Phase 4 audits the full diff for issues beyond the original request
- "Max 3 skill files" changed to max 3 reference files beyond SKILL.md (added self-verification.md); delegated skill files don't count
- Guard step clarified for features (edge case coverage, not recurrence prevention) and checks for existing guardrails before adding duplicates
- Graceful degradation entry renamed from "Large context window" to "Context pressure" with 30% threshold

### Added
- **Self-verification at Ready Gate:** Agent loads `references/self-verification.md` and walks a pipeline compliance ledger to verify every required step was completed. Missing security checks block shipping. Compliance score reported in change summary.
- **Progress logging (LOG lines):** Agent emits `LOG: [Phase.Step] Description` lines during work with concrete details (file names, counts, findings). ANNOUNCE lines remain as phase-exit summaries.
- `references/self-verification.md` — execution ledger templates for Quick/Standard/Full modes, compliance check algorithm, LOG format spec
- Eval 16: self-verification and logging behavior
- Mid-pipeline abort: `git checkout -- .` to discard changes, offer branch deletion on "stop"/"undo"/"cancel"
- Monorepo awareness: auto-detect and scope tests/scans to affected packages
- PR description template: structured ## What/Why/Testing/Guardrails/Breaking Changes
- CHANGELOG automation: auto-generate entry from commit message
- Context window awareness: summarize rather than load in full when files exceed ~30% of available context
- Delegation fallback: skip delegation if installed skills list not available in context
- Agent Compatibility section in README (agentic vs chat-only)
- Quick mode Phase 4 (Ship) now has explicit HARD STOP

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
