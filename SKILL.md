---
name: sdlc-autopilot
description: Full software development lifecycle orchestrator for ANY coding task. Triggers on ALL code changes — bug fixes, features, refactors, improvements, performance, security fixes, API changes, UI changes, database changes, config changes, new files, deletions, or any request to modify, create, fix, build, or ship code. This skill should activate FIRST on every coding prompt to orchestrate the full pipeline — understand, plan, implement, test, audit, guard against recurrence, and ship. It automatically discovers and delegates to other installed skills for domain expertise.
license: MIT
---

# SDLC Autopilot

Transforms any rough prompt into a full SDLC execution — tailored to risk.
The user types one messy sentence. You deliver deploy-ready, tested, audited,
guarded code where every fix is protected against recurrence.

**Principles:** (1) Tailored to risk, never one-size-fits-all. (2) Token-frugal — every token earns its keep. (3) User provides the prompt, everything else is automatic. (4) Fix it, guard it, test the guard, verify. (5) Respect project conventions and installed skills. (6) Fail safe — never auto-deploy, warn before committing to main/master (user can override), never expose secrets.

**Token budget:** The agent loads the full SKILL.md (~4,000 tokens) on activation. Per-mode execution overhead: Quick ~1,500 tokens, Standard ~2,500 tokens, Full ~4,000 tokens (also loads deep-audit.md). Deploy add-on ~600 tokens (loads deployment.md once). Self-verification add-on ~800 tokens (loaded at Ready Gate). These budgets represent the instructions the agent follows per mode, not including user code reading or tool calls. Max 4 reference files loaded per invocation (SKILL.md + deep-audit.md + deployment.md + self-verification.md). Delegated skill files do not count toward this limit.

---

## The Fix-Guard-Test-Verify Loop

This is the core innovation. It applies to EVERY issue — the original request AND anything found during audit. Without this loop, bugs get patched but recur. With it, every fix is permanent.

**The 5 steps:**

1. **FIX** the issue. Apply the code change.
2. **ROOT CAUSE:** Why did this happen? Is it a pattern? Grep for the same pattern elsewhere. If found → fix up to 5 occurrences, note the rest. This is a single grep — cheap, but catches systemic issues.
3. **GUARD:** Prevent this CLASS of issue from recurring. For features, focus guards on edge case coverage and contract tests rather than recurrence prevention. If a guardrail already exists for this class of issue (e.g., the project already uses parameterized queries), verify it covers the current case rather than adding a duplicate. Choose the lightest effective guardrail using this priority (use the FIRST viable):
   - Type/compiler enforcement (caught at build time)
   - Linter/static analysis rule (caught before tests)
   - Runtime assertion/invariant (caught at test/runtime)
   - Targeted test (caught during test suite)
   - Code comment at danger point (caught during review)
4. **TEST THE GUARD:** Write tests that verify: the fix works, the guardrail catches recurrence, and edge cases are covered.
5. **VERIFY:** Run the targeted tests. Pass → continue. Fail → fix and loop back to step 1. Existing tests break → circuit breaker (revert, note as deferred).

**Proportionality rules — match effort to severity:**

- **STRUCTURAL** (logic error, security hole, missing validation, race condition, data corruption): Full loop — Fix + Root cause + Guard + Test + Verify
- **BEHAVIORAL** (missing error handling, incomplete edge case, wrong return value): Partial loop — Fix + Guard + Test + Verify (skip root cause scan)
- **COSMETIC** (naming, formatting, minor DRY, style): Quick/Standard → Fix only. Full mode → Fix + code comment guard.
- **SECURITY findings ALWAYS get the full loop regardless of severity. No exceptions.**

---

## Mode Selection

**Signal 1 — Risk classification:**
- LOW → Quick: text/copy, color/style, config values, comments, simple renames, docs-only
- MEDIUM → Standard: bug fixes, new UI components, new functions, form fields, validation, behavior-preserving refactors
- HIGH → Full: auth/authz, payments, PII/data handling, API changes, DB schema, shared libraries, security fixes, deployment config, env vars, multi-service

**Signal 2 — User language:**
- "just", "quick", "simple", "only" → bias Quick
- "careful", "thorough", "full", "make sure", "full pipeline", "full audit", "full sdlc" → Full mode
- No signal → use risk classification
- Explicit override always wins

**Hard rules:**
- HIGH risk can NEVER be Quick mode, even if user asks. Explain why and offer Standard as the lightest option.
- User can ALWAYS force Full mode regardless of risk level. If user says "full pipeline", "full audit", "full sdlc", or explicitly requests the complete pipeline — use Full mode even for low-risk changes.

---

## Quick Mode (4 Phases)

**PHASE 1: UNDERSTAND** — Read relevant file(s) (usually 1-2). Confirm what needs to change. If ambiguous → ask ONE question, then proceed. ANNOUNCE: "Quick fix: [brief description]."

**PHASE 2: IMPLEMENT** — Make the change following existing conventions. Delegate to relevant installed skills if applicable. Run the fix-guard-test loop (lightweight): fix the issue, add a brief code comment if non-obvious. Guardrail and root cause scan are OPTIONAL in quick mode. ANNOUNCE: "Change applied."

**PHASE 3: VERIFY** — Run linter/formatter if available → auto-fix. Run existing test suite if available. If tests fail due to our change → fix. Quick check: does this affect anything else? ANNOUNCE: "Verified. Tests pass."

**PHASE 4: SHIP** — **HARD STOP.** Self-verify: load references/self-verification.md, walk Quick ledger, flag gaps. Present one-line summary: "Changed X in file Y. Tests pass. Pipeline: N/N steps." Wait for user confirmation before proceeding. If on main/master → warn: "You are on main. Creating branch type/short-description. Say 'commit to main' to override." If user overrides → commit to main. Commit with conventional message, push to branch. Deploy if applicable.

---

## Standard Mode (7 Phases — The Default)

### PHASE 1: UNDERSTAND & PLAN
Why: Misunderstanding the request wastes everything downstream.

1. Parse intent: bug-fix | feature | improvement | refactor | performance
2. Scan codebase for relevant context:
   - List file tree (2 levels, respect .gitignore)
   - Grep for keywords from user's prompt
   - Read ONLY directly relevant files (cap: ~10 files). If files exceed ~30% of available context → read key sections or summarize rather than loading in full. Prioritize files directly mentioned in the user's prompt.
   - Check for project rules: .cursorrules, CONTRIBUTING.md, .editorconfig
3. Scan available skills for ANY installed skill relevant to this change
4. Generate Implementation Brief:
   - Problem statement (rewritten clearly)
   - Root cause hypothesis (for bugs)
   - Acceptance criteria (3-5 testable conditions)
   - Files to change and regression risks
   - Skills to delegate to (if any)
5. Plan implementation steps (numbered, concise)
6. Plan test strategy (what types, what edge cases)

EXIT: If bug can't be found or request is genuinely ambiguous → ask ONE clarifying question. Never guess between equally likely options.

ANNOUNCE: "[intent type] identified. Implementing [N] steps."

### PHASE 2: IMPLEMENT
Why: Disciplined implementation prevents scope drift and keeps changes reviewable.

1. Git branch check (if git repo): if on main/master → warn: "You are on main. Creating branch type/short-description. Say 'commit to main' to override." If user overrides → stay on main. If already on a feature/dev/other branch → stay on it and commit there.
2. Execute plan step-by-step
3. Delegate to relevant installed skills: scan available_skills — if ANY skill's description matches the domain, read its SKILL.md and follow it. Always scan. Never hardcode.
4. Follow existing project conventions
5. If new dependencies: install, note for summary
6. If DB schema changes: create migration file

RULES: SCOPE CONTROL — implement ONLY what the plan specifies. Note unrelated improvements in summary but do NOT change them. Never expose secrets. Respect project rules found in Phase 1.

ANNOUNCE: "Implementation complete. Running checks."

### PHASE 3: GATE & TEST
Why: Catching issues here is 10x cheaper than catching them in production.

1. Run linter → auto-fix fixable issues
2. Run formatter → auto-fix
3. Run type checker → fix type errors in changed files
4. Run existing test suite: failures from our change → fix; pre-existing failures → note and ignore
5. Apply fix-guard-test-verify loop to the ORIGINAL request:
   a. Confirm the fix is in place
   b. Root cause: why did this bug/gap exist? Same pattern elsewhere? (single grep) If found → fix up to 5, note rest
   c. Guard: add the lightest effective guardrail (type > linter > assertion > test > comment)
   d. Write targeted tests: regression test for original issue, test that guardrail works, edge cases
   e. Verify: run new tests → must pass
6. Update existing tests whose expectations intentionally changed (add comment explaining WHY)
7. Run ALL tests (new + existing) to confirm

IF PROJECT HAS NO TOOLING: skip linter/formatter/typechecker, still write tests in logical format, suggest framework but don't block pipeline.

GATE CAP: 3 auto-fix cycles max, then proceed to audit.

ANNOUNCE: "N tests pass (M new, K guardrail). Linting clean."

### PHASE 4: AUDIT (2 passes)
Why: Self-review catches what implementation missed. Phase 3 handled the original request; this phase audits the FULL diff for issues beyond that — things introduced during implementation, missed edge cases, and security concerns. The loop ensures every finding is permanently fixed, not just patched.

**Pass 1 — Correctness Checklist:** Walk through each item mechanically against the diff. Do NOT rely on general "does this look right" judgment — check each item explicitly.
- [ ] Each acceptance criterion satisfied? (check one by one)
- [ ] Off-by-one errors in loops/indices?
- [ ] Null/undefined access on any new variable or return value?
- [ ] Race conditions on shared state or async operations?
- [ ] Error handling: every new call site has a failure path?
- [ ] If API changed: grep for callers, verify compatibility
- [ ] Hardcoded values that should be config/env vars?

For each STRUCTURAL finding → apply the fix-guard-test-verify loop:
  1. Fix it
  2. Root cause: same pattern elsewhere? (grep) Fix up to 5, note rest
  3. Guard: add guardrail for this CLASS of issue
  4. Test: write test that catches this finding AND verifies the guardrail
  5. Verify: run new test → must pass

For each BEHAVIORAL finding → Fix + Guard + Test + Verify (skip root cause scan)
For each COSMETIC finding → Fix only. No guardrail needed.

Run tests after all pass-1 fixes.

**Pass 2 — Security & Quality Checklist:** Walk through each item mechanically against the diff.
- [ ] Input validation: every new user input sanitized/validated?
- [ ] Injection: raw SQL, eval(), innerHTML, dangerouslySetInnerHTML?
- [ ] Auth: new endpoints have auth + authz checks?
- [ ] Secrets: no hardcoded secrets, tokens, API keys?
- [ ] XSS/CSRF: output encoding, CSRF tokens on mutations?
- [ ] Performance: N+1 queries, unnecessary re-renders, memory leaks (obvious only)?
- [ ] Accessibility (UI changes): keyboard nav, ARIA labels?
- [ ] Code quality: naming, DRY, complexity (don't gold-plate)?

For each finding → same fix-guard-test-verify loop with same proportionality rules. Security findings ALWAYS get the full loop regardless of severity. Security guardrails are mandatory.

Run tests after all pass-2 fixes.

CIRCUIT BREAKER: If fixing a finding causes a NEW test failure → REVERT THE FIX. Note in summary as "identified but not fixed — requires manual review." Do not enter a fix-break spiral.

ANNOUNCE: "Audit done. N issues: fixed M, guarded K, tested J."

### PHASE 5: REGRESSION & FINAL VERIFICATION
Why: This is the last line of defense. Verify everything works together and no guardrails were accidentally removed during later fixes.

1. Run FULL test suite (new + existing + guardrail tests) — the ONLY full-suite run post-implementation
2. If regressions: expected (behavior change) → update test with explanation; unexpected → fix with guard-test-verify loop, re-run
3. Verify wiring: imports, exports, routes, API endpoints
4. **Guardrail completeness check** — for each issue fixed in Phases 3-4, confirm:
   a. The fix is present and correct
   b. The guardrail is in place (not accidentally removed during later fixes)
   c. The guardrail test exists and passes
   This is a COMPLETENESS CHECK, not a re-audit. Quick scan.
5. If applicable: add error logging for new error paths
6. Update documentation ONLY IF the change affects it: README, API docs, inline comments for non-obvious logic, CHANGELOG

ANNOUNCE: "All N tests pass. M guardrails verified. Docs updated."

### PHASE 6: READY GATE
Why: The user sees exactly what happened and decides what's next. This phase also verifies the pipeline itself was followed correctly.

1. **Self-verification:** Read references/self-verification.md. Walk the execution ledger for the current mode. Check every step was completed or has a valid skip reason. Report compliance: "Pipeline Compliance: N/M steps completed." If security steps were skipped → BLOCK shipping and run them first. Other gaps → warn and let user decide.

2. **Generate change summary:**
   - What was done (1-2 sentences)
   - Files changed (list with one-line descriptions)
   - Tests: N new, M updated, K guardrail tests
   - Issues found during audit: N total (fixed and guarded: M, fixed only/cosmetic: K, deferred/circuit breaker: J with descriptions)
   - Root cause patterns found elsewhere: N (with brief list)
   - Guardrails added: N (with brief descriptions)
   - Pipeline compliance: N/M steps (with any gaps listed)
   - Dependencies added / Migrations created (if any)
   - Pre-generated conventional commit message
   - Pre-generated branch name

**HARD STOP. Wait for user:**
- "ship it" / "push" / "deploy" / "looks good" → Phase 7
- "change X" / "also do Y" → return to Phase 2
- "cancel" / "revert" → discard branch
- "create PR" → Phase 7 with PR

LOG: "[P6.1] Self-verification: N/M steps completed [✅|⚠️]"
ANNOUNCE: "Ready gate passed. Summary above."

### PHASE 7: SHIP
1. Git: stage, commit with conventional message, push branch
2. If "create PR": create PR with structured description:
   ```
   ## What
   [1-2 sentence summary from Phase 6]
   ## Why
   [Root cause / motivation]
   ## Testing
   [N new tests, M guardrail tests, what they cover]
   ## Guardrails Added
   [List of guardrails preventing recurrence]
   ## Breaking Changes
   [None / list of breaking changes]
   ```
3. Update CHANGELOG if project has one: add entry under `[Unreleased]` using conventional commit type (Added/Fixed/Changed/Security). Auto-generate from the commit message.
4. If deployment needed: read references/deployment.md for detected platform, deploy. If deploy fails → attempt rollback using platform's rollback command (see deployment.md), capture error, DO NOT retry, present to user
5. Post-deploy: health check if platform supports it

ANNOUNCE: "Pushed to [branch]. Commit: [hash]."

---

## Full Mode Additions

Identical to Standard with these additions:

**PHASE 1:** User checkpoint — present the plan, wait for explicit approval before implementing. Critical-risk changes never skip this.

**PHASE 4:** Add Pass 3 — Convergence: re-review ALL changes from passes 1-2. Verify every structural fix has guardrail AND test. If structural issues remain → fix with full loop (max 3 retries). If stuck → escalate to user. Security Deep Dive: read references/deep-audit.md, OWASP Top 10 review, auth/authz flow verification, data handling (encryption, PII, logging), dependency vulnerability assessment. Every security finding gets FULL loop — no exceptions. CONVERGENCE SHORTCUT: If pass 1 AND pass 2 both find zero issues → skip pass 3. Pass 1 results do NOT gate pass 2 thoroughness — correctness and security are independent concerns.

**PHASE 5:** Guardrails mandatory for ALL findings including cosmetic. Architectural guardrails encouraged (linter rules, pre-commit hooks). Root cause scan radius expanded.

---

## Dynamic Skill Delegation

This skill is the orchestrator — it decides WHAT work to do and in WHAT order. Other installed skills provide specialized expertise for HOW to do it.

**Phase 1 — Discovery:** At startup the agent loads the name and description of ALL installed skills into context. Review this list ONCE. For each skill whose description matches the domain of the current change (e.g. a React skill for React work, a testing skill for test writing, a design skill for UI changes) → note it in the Implementation Brief as a skill to delegate to.

**Phase 2 — Delegation:** When you reach work matching a noted skill's domain → read that skill's SKILL.md and follow its instructions for that portion of the implementation. For example, if the user has a `frontend-design` skill installed and the task involves UI, load and follow that skill's guidance for the CSS/design work.

**Rules:** Always check the installed skills list — never assume what the user has. If none are relevant → proceed with your own best judgment. If multiple are relevant → use each for its respective domain. This skill remains in control of the overall pipeline (phases, testing, auditing). Delegated skills handle domain-specific best practices.

**Fallback:** If the installed skills list is not available in context (some agents don't expose it) → skip delegation entirely and proceed with your own best judgment. Do not error or stall.

---

## Critical Behaviors

**Follow-ups:** Pipeline shipped → start NEW pipeline. During ready gate → treat as "change X," return to Phase 2. "revert"/"undo" → git revert, done. Each invocation is STATELESS.

**Mid-pipeline abort:** If user says "stop", "undo everything", or "cancel" at ANY point mid-pipeline → immediately stop. If changes were made to files: `git checkout -- .` to discard all unstaged changes (or `git stash` if user might want them later). If a branch was created: offer to delete it. Confirm: "All changes reverted. Back to clean state."

**Monorepos:** If workspace root contains `packages/`, `apps/`, `libs/`, `pnpm-workspace.yaml`, or `lerna.json` → treat as monorepo. Phase 1: identify affected package(s) only. Phase 3: run tests ONLY in affected packages (`--filter`, `--scope`, or `cd packages/X && npm test`). Root cause scans: search within the affected package first, then cross-package only if the pattern is in shared code.

**Large codebases (10,000+ files):** List top-level tree (2 levels). Grep for keywords. Read ONLY grep results + direct imports. Cap ~10 files in Phase 1. Root cause scans use grep only — never scan entire codebase file-by-file.

**Project rules conflict:** Read project rules in Phase 1. SDLC provides the PROCESS. Project rules provide the STANDARDS. If conflict: project rules win for style, SDLC wins for process.

**Can't find the bug:** Report what was searched and found. Ask ONE specific question. Do NOT guess or "fix" something that might not be the issue.

**Secrets:** Never include secrets in output or commits. Never add .env to git. Reference by variable name only. Exposed secrets → flag as audit finding with full loop (guard: .gitignore + pre-commit check).

---

## Graceful Degradation

- No shell commands → write tests + list commands for user. All phases still happen.
- No test framework → write tests in logical format. Suggest framework, don't block. Guardrail tests still written.
- No linter/formatter/typechecker → skip automated gates. Suggest setup, don't insist.
- No git → skip branching/commits/push. All other phases still happen.
- Context pressure (many/large files) → if files exceed ~30% of available context, summarize rather than load in full. Prioritize files from user's prompt. Don't load reference files unless full mode.

---

## Progress Logging & Self-Verification

**Two types of user-facing output during execution:**

1. **LOG lines** — emitted DURING work. Format: `LOG: [Phase.Step] Description`. Concrete details: file names, counts, findings. Every phase gets at least one LOG. If a step is skipped, LOG why. Keep under 80 chars.
2. **ANNOUNCE lines** — emitted at END of each phase. One line, 15 words max. Phase-exit summary.

**Self-verification:** At the Ready Gate (Phase 6 for Standard/Full, Phase 4 for Quick), load references/self-verification.md and check the execution ledger. The agent verifies it actually performed every required step for the chosen mode. Gaps are reported to the user. Missing security checks block shipping.

**Examples:**
```
LOG: [P1.1] Parsed intent: bug-fix in SearchPage component
LOG: [P1.2] Scanned 3 files: SearchPage.jsx, SearchPage.css, test file
ANNOUNCE: "Bug fix identified. Implementing 2 steps."
LOG: [P2.1] On branch fix/search-keyboard — safe to commit
LOG: [P2.2] Step 1/2: Fixed keyboard handler in SearchPage.jsx
ANNOUNCE: "Implementation complete. Running checks."
LOG: [P6.1] Self-verification: 22/22 steps completed ✅
ANNOUNCE: "Ready gate passed. Summary above."
```
