---
name: sdlc-autopilot
description: "SDLC pipeline for AI coding agents — turns any prompt into tested, guarded code. Risk-based modes (Quick/Standard/Full). Core: Fix-Guard-Test-Verify loop guards every fix against recurrence. AI-assisted review with honest limitations. Auto-detects toolchains, degrades gracefully. Any language, any agent."
license: MIT
---

# SDLC Autopilot

One messy prompt in. Tested, guarded, reviewed code out.

**Principles:** Risk-proportional. Token-frugal. Fix it, guard it, test the guard. Respect project conventions. Never auto-deploy or expose secrets. Honest about limitations — AI review catches known patterns, not novel vulnerabilities. Cooperate with the agent — phases are outcomes, not rituals.

**Token budget:** SKILL.md (~3,200 tokens) loaded on activation. Reference files loaded only when needed: self-verification.md (~1,500 tokens, Ready Gate), deep-audit.md (~1,900 tokens, Full mode), deployment.md (~2,200 tokens, deploy phase). Max 3 reference files per invocation beyond SKILL.md.

---

## AI Review Limitations — Read First

This pipeline includes AI-assisted code review. It is NOT a professional security audit or expert human review.

**CAN catch:** known vulnerability patterns (SQLi, XSS, injection), missing null checks, off-by-one, hardcoded secrets, missing validation, known anti-patterns (eval, innerHTML), basic auth gaps.

**CANNOT catch:** novel attack vectors, business logic flaws, subtle race conditions, cryptographic errors, context-dependent security issues, anything requiring full-system understanding.

**Rules:** Never say "security audit passed" — say "AI-assisted review complete." Every change summary includes the limitations line. HIGH-RISK domains (auth, payments, PII, crypto, medical, legal) require: "HUMAN REVIEW RECOMMENDED: This change touches [domain]."

---

## Fix-Guard-Test-Verify Loop

The core mechanism. Applies to the original request and every issue found during review. Cosmetic edits stay proportional.

1. **FIX** the issue.
2. **ROOT CAUSE:** Why did this happen? Grep for the same pattern elsewhere. For each match: read the call site — fix ONLY confirmed bugs (same risk, no existing guard). Skip false positives with reason. Cap: 5 fixes. If >5 confirmed, triage by severity, fix top 5, report rest. Report: grep pattern, N matches, M fixed, K skipped.
3. **GUARD:** Prevent this CLASS of issue. If a guardrail already exists, verify it covers this case. Choose the lightest effective guard: type/compiler > linter rule > runtime assertion > targeted test > code comment (last resort).
4. **TEST THE GUARD.** Every test must satisfy:
   - **Inversion:** Would this test FAIL on the pre-fix code? If not, rewrite it.
   - **Behavior:** Assert on outputs/side-effects/errors, not internal calls or mock counts.
   - **Negative case:** At least one test with bad/edge/boundary input.
   - **Minimal mocking:** Only mock external I/O (network, DB, filesystem).
5. **VERIFY:** Run tests. Pass → continue. Fail → retry (max 3 attempts). Existing tests break → revert fix, note as deferred. After 3 failed retries → defer to user.

**Proportionality:** STRUCTURAL (logic, security, race condition) → full loop. BEHAVIORAL (missing error handling, wrong return) → fix + guard + test + verify. COSMETIC (naming, formatting) → fix only. Security findings ALWAYS get the full loop.

---

## Mode Selection

Security/auth/payments/PII/crypto/deployment/DB schema → **Full**. Always. Never downgrade.
User forces "full"/"thorough"/"careful" → **Full**. Always allowed.
Bug fixes, new components, validation, refactors → **Standard**.
Text, color, config, comments, docs, simple renames → **Quick**.
Ambiguous → **Standard**. "Just"/"quick" in user prompt biases toward Quick but never below the safe floor.

State the mode and reason if non-obvious.

---

## Quick Mode (Trivial Changes)

**Single-value, single-file changes** (color, string, config) with no behavior impact: Read file → change → verify (lint + tests if available) → one-line summary with "AI-reviewed, not human-audited." → HARD STOP for user confirmation.

**Promotion:** If the work requires multiple files, behavior changes, tests, or guardrails → promote to Standard immediately. Do not stay in Quick mode with a partial pipeline.

Branching: if on main/master → warn, offer to create branch. User can override with "commit to main."

---

## Standard Mode (5 Phases)

### PHASE 1: UNDERSTAND

1. Parse intent (bug-fix / feature / refactor / performance / improvement).
2. Explore the codebase: relevant files, project rules (.cursorrules, CONTRIBUTING.md, .editorconfig), installed skills.
3. Produce an Implementation Brief: problem statement, root cause hypothesis (bugs), 3-5 acceptance criteria, edge-case matrix (relevant boundaries and failure modes), files to change, skills to delegate to.
4. Plan implementation steps and test strategy.

If ambiguous → ask ONE clarifying question. Never guess between equally likely options.

### PHASE 2: IMPLEMENT

1. Branch check: if on main/master → warn, offer branch creation. User can override.
2. For structural/security work with existing test harness: write the failing test FIRST. If blocked (no harness, nondeterminism, external dependency), state the specific reason and add the test immediately after the fix.
3. Execute plan. Follow project conventions. Delegate to relevant installed skills for domain work.
4. Scope control: implement ONLY what the plan specifies. Note unrelated improvements but don't change them.

### PHASE 3: VERIFY

1. Run linter/formatter/type-checker → auto-fix (max 3 cycles).
2. Run existing test suite. Our failures → fix. Pre-existing failures → note and ignore.
3. Apply Fix-Guard-Test-Verify loop to the original request.
4. **Audit the full diff** for issues beyond the original request. Walk these mechanically:
   - Correctness: acceptance criteria met, off-by-one, null/undefined, race conditions, error handling, API compatibility.
   - Security: input validation, injection, auth on new endpoints, secrets, XSS/CSRF, performance (N+1, leaks), accessibility.
   Each finding → Fix-Guard-Test-Verify loop with proportionality rules. Circuit breaker: if fixing a finding causes a NEW test failure → revert, note as deferred.
5. Verify edge-case matrix: every item is tested, guarded, impossible by construction, or explicitly deferred as unresolved risk. Structural/security deferrals block shipping.
6. Run ALL tests. Confirm all pass.
7. Verify guardrail completeness: every fix still has its guard and test after all edits.

### PHASE 4: READY GATE

1. Run `scripts/verify-pipeline.sh standard` if shell available — present RAW output.
2. Self-assess: read references/self-verification.md, walk outcome checklist. Missing security outcomes → BLOCK.
3. If script and self-assessment disagree: state the contradiction, diagnose, fix, re-run. Script is authoritative.
4. Generate change summary: what done, files changed, tests (N new, M updated), edge cases covered, deferred risks, review findings, guardrails added, verification result, limitations line (MANDATORY), human review recommendation if high-risk, commit message + branch.
5. Generate cross-model review prompt (copyable, self-contained, with diff and 6 adversarial tasks). Standard: "Recommended." Full/HIGH-RISK: "Strongly recommended."

**HARD STOP.** Wait for user: "ship it" → Phase 5. "change X" → Phase 2. "cancel" → discard.

### PHASE 5: SHIP

1. Stage, commit (conventional message), push branch.
2. If "create PR": create PR with What/Why/Testing/Guardrails/Breaking Changes sections.
3. Update CHANGELOG if project has one.
4. If deployment requested: read references/deployment.md. **NEVER auto-deploy.** Present: detected platform, environment, exact command. Wait for explicit approval. Default to preview/staging; production requires explicit "prod."

---

## Full Mode Additions

Everything in Standard, plus:

**PHASE 1:** Present plan to user, wait for explicit approval before implementing.

**PHASE 3:** Add a convergence pass after the initial audit — re-review ALL changes, verify every structural fix has guardrail + test. Load references/deep-audit.md for OWASP Top 10 pattern review, auth flow verification, data handling audit. Convergence shortcut: if audit found 0 issues, skip convergence. Guardrails mandatory for ALL findings including cosmetic.

---

## Engineering Standards (Standard + Full)

1. **TDD bias:** Failing test first if feasible. If not, state the specific blocker.
2. **Single source of truth:** Reuse canonical schema/type/validator/config. No parallel definitions unless justified as defense-in-depth.
3. **DRY with judgment:** Remove duplication the change introduces. Don't abstract single uses.
4. **Contract safety:** Public API/data model/config changes → update callers or compatibility path.
5. **Smallest safe change:** Fix root cause, no speculative refactors.

---

## Dynamic Skill Delegation

Phase 1: scan installed skills. Phase 2: when reaching domain-specific work → read that skill's SKILL.md and follow it. This skill controls the pipeline; delegated skills handle domain practices. No relevant skills → use own judgment.

---

## Safety & Edge Cases

- **Secrets:** Never in output or commits. Reference by variable name only.
- **Main/master:** Always warn before committing. User can override.
- **Deploy:** NEVER without showing command and getting approval. Default preview/staging.
- **Can't find the bug:** Report what was searched. Ask ONE question.
- **Monorepos:** Auto-detect (packages/, apps/, pnpm-workspace.yaml). Scope tests/scans to affected packages.
- **Large codebases:** Read only relevant files. Root cause scans use grep.
- **No tooling:** Skip automated gates. Write tests in logical format. Suggest framework, don't block.
- **No shell:** Write tests + list commands for user. Self-verify inline.
- **Follow-ups:** Pipeline shipped → new pipeline. "Change X" at gate → Phase 2.
- **Abort:** "stop"/"cancel" → revert pipeline changes (ask first if pre-existing edits exist). Offer branch deletion.
- **Agent cooperation:** Phases are outcomes. If the agent already handles branching/testing/committing natively, use its mechanics. This skill adds the loop, audit, and verification — not duplicate infrastructure.
- **Project rules vs SDLC:** Style conflicts → project rules win. Process conflicts → SDLC wins.
