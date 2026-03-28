# Self-Verification — Pipeline Compliance Check

Loaded at Ready Gate (Phase 6) and Quick mode Phase 4. The agent checks its own execution ledger against the expected process for the chosen mode.

---

## Execution Ledger Template

The agent maintains this ledger mentally throughout execution. At the Ready Gate, it reviews the ledger and flags any gaps.

### Quick Mode Ledger
```
PIPELINE: Quick | Risk: [LOW] | Started: [timestamp/phase]
─────────────────────────────────────────────────────
[P1] UNDERSTAND
  □ Read relevant file(s): [list]
  □ Confirmed what needs to change: [yes/no]
  □ Ambiguity resolved: [N/A | asked question]
  □ LOG emitted: [yes/no]

[P2] IMPLEMENT
  □ Change made: [file(s)]
  □ Followed existing conventions: [yes/no]
  □ Skill delegation checked: [delegated to X | none relevant | list unavailable]
  □ LOG emitted: [yes/no]

[P3] VERIFY
  □ Linter/formatter run: [pass | N/A]
  □ Tests run: [N pass | N/A]
  □ Side effects checked: [yes/no]
  □ LOG emitted: [yes/no]

[P4] SHIP
  □ Summary presented to user: [yes/no]
  □ Branch safety check: [on feature branch | warned about main | user overrode]
  □ User confirmation received: [yes/no]
```

### Standard Mode Ledger
```
PIPELINE: Standard | Risk: [LOW/MEDIUM/HIGH] | Intent: [type]
─────────────────────────────────────────────────────
[P1] UNDERSTAND & PLAN
  □ Intent parsed: [bug-fix | feature | improvement | refactor | performance]
  □ Codebase scanned: [N files read]
  □ Skills checked: [delegated to X | none relevant | list unavailable]
  □ Implementation brief generated: [yes/no]
    - Acceptance criteria: [N items]
    - Files to change: [list]
  □ Test strategy planned: [yes/no]
  □ LOG emitted: [yes/no]

[P2] IMPLEMENT
  □ Branch check: [on feature branch | warned about main | user overrode]
  □ Plan steps executed: [N of M]
  □ Skills delegated: [list | none]
  □ Scope control: [stayed within plan | noted extras for summary]
  □ LOG emitted: [yes/no]

[P3] GATE & TEST
  □ Linter run: [pass | fixed N | N/A]
  □ Formatter run: [pass | fixed N | N/A]
  □ Type checker run: [pass | fixed N | N/A]
  □ Existing tests: [N pass | N fail from our change (fixed) | N pre-existing]
  □ Fix-Guard-Test-Verify loop applied to original request:
    - Fix confirmed: [yes/no]
    - Root cause scanned: [pattern found N times | no pattern]
    - Guardrail added: [type: description]
    - Tests written: [N regression, N guardrail, N edge case]
    - Tests verified: [all pass]
  □ LOG emitted: [yes/no]

[P4] AUDIT
  □ Pass 1 (Correctness) run: [yes/no]
    - Findings: [N structural, N behavioral, N cosmetic]
    - Each finding looped: [yes/no]
  □ Pass 2 (Security) run: [yes/no]
    - Findings: [N structural, N behavioral, N cosmetic]
    - Each finding looped: [yes/no]
    - Security findings got full loop: [yes | N/A]
  □ Circuit breaker triggered: [N times | never]
  □ Tests run after each pass: [yes/no]
  □ LOG emitted: [yes/no]

[P5] REGRESSION & VERIFICATION
  □ Full test suite run: [N pass, N fail]
  □ Regressions fixed: [N | none]
  □ Wiring verified (imports, routes, exports): [yes/no]
  □ Guardrail completeness check:
    - All fixes still present: [yes/no]
    - All guardrails still present: [yes/no]
    - All guardrail tests pass: [yes/no]
  □ Docs updated: [list | N/A]
  □ LOG emitted: [yes/no]

[P6] READY GATE
  □ Change summary generated: [yes/no]
  □ Self-verification run: [yes/no] ← THIS CHECK
  □ All ledger items satisfied: [yes/no]
  □ Gaps flagged to user: [list | none]

[P7] SHIP (if triggered)
  □ Committed: [hash]
  □ Pushed: [branch]
  □ PR created: [yes/no | N/A]
  □ CHANGELOG updated: [yes/no | N/A]
  □ Deployed: [yes/no | N/A]
  □ Health check: [pass | N/A]
```

### Full Mode Additions to Ledger
```
[P1] ADDITIONS
  □ User checkpoint: plan presented and approved: [yes/no]

[P4] ADDITIONS
  □ Pass 3 (Convergence) run: [yes/no | skipped — zero findings in audit passes 1+2]
    - Structural issues remaining: [N | none]
  □ Security Deep Dive: [yes/no]
    - deep-audit.md loaded: [yes/no]
    - OWASP Top 10 reviewed: [yes/no]
    - Auth/authz flow verified: [yes/no]
    - Data handling checked: [yes/no]
    - Dependencies assessed: [yes/no]

[P5] ADDITIONS
  □ ALL findings (including cosmetic) have guardrails: [yes/no]
  □ Architectural guardrails considered: [added N | none needed]
```

---

## Compliance Check Algorithm

At the Ready Gate, the agent performs this check:

1. **Walk the ledger** for the current mode (Quick/Standard/Full)
2. For each checkbox:
   - ✅ Completed → pass
   - ⚠️ Skipped with valid reason (e.g., "N/A — no test framework") → pass with note
   - ❌ Not done, no valid reason → **compliance gap**
3. **Report gaps** to the user in the Ready Gate summary under a "Pipeline Compliance" section:
   ```
   ## Pipeline Compliance
   ✅ 22/23 steps completed
   ⚠️ 1 step skipped with reason:
     - Formatter: N/A — no formatter configured
   ```
   OR if there are gaps:
   ```
   ## Pipeline Compliance
   ⚠️ 20/23 steps completed — 3 gaps:
     - [P3] Root cause scan not performed
     - [P4] Pass 2 security checklist not run
     - [P5] Guardrail completeness check skipped
   Recommendation: Re-run phases 3-5 to close gaps.
   ```

4. **Severity of gaps:**
   - Missing security checks → **BLOCK shipping**. Tell user: "Security verification incomplete. Running security pass before ship."
   - Missing audit pass → warn strongly but allow user override
   - Missing cosmetic steps → note only
   - Missing tests → warn, offer to write them

5. **Quick mode**: The ledger is shorter. Compliance check is lighter. Missing verify step → warn. Everything else → note.

---

## LOG Format

Throughout execution, the agent emits LOG lines to keep the user informed of progress. These are distinct from ANNOUNCE lines (which are phase-exit summaries).

**Format:** `LOG: [Phase.Step] Description`

**Examples:**
```
LOG: [P1.1] Parsed intent: bug-fix in SearchPage component
LOG: [P1.2] Scanned 3 files: SearchPage.jsx, SearchPage.css, SearchPage.test.jsx
LOG: [P1.3] No relevant installed skills found
LOG: [P1.4] Implementation brief: 2 acceptance criteria, 1 file to change
ANNOUNCE: "Bug fix identified. Implementing 2 steps."

LOG: [P2.1] On branch fix/search-keyboard — safe to commit
LOG: [P2.2] Step 1/2: Fixed keyboard handler in SearchPage.jsx
LOG: [P2.3] Step 2/2: Updated event binding
ANNOUNCE: "Implementation complete. Running checks."

LOG: [P3.1] ESLint: pass (0 errors)
LOG: [P3.2] Prettier: 1 file reformatted
LOG: [P3.3] Existing tests: 4 pass
LOG: [P3.4] Root cause scan: found same pattern in 2 other files — fixed
LOG: [P3.5] Guardrail: added keyboard event assertion
LOG: [P3.6] New tests: 2 regression, 1 guardrail — all pass
ANNOUNCE: "7 tests pass (3 new, 1 guardrail). Linting clean."

LOG: [P4.1] Pass 1 correctness: 1 behavioral finding (missing error case)
LOG: [P4.2] Fixed + guarded + tested behavioral finding
LOG: [P4.3] Pass 2 security: no findings
ANNOUNCE: "Audit done. 1 issue: fixed 1, guarded 1, tested 1."

LOG: [P5.1] Full test suite: 8 pass, 0 fail
LOG: [P5.2] Guardrail completeness: 2/2 guardrails verified
ANNOUNCE: "All 8 tests pass. 2 guardrails verified. Docs updated."

LOG: [P6.1] Self-verification: 22/22 steps completed ✅
ANNOUNCE: "Ready gate passed. Summary above."
```

**Rules:**
- LOG lines are informational — they appear DURING work, not after
- ANNOUNCE lines are summaries — they appear at the END of each phase
- Every phase gets at least one LOG line
- LOG lines should be concrete: include file names, counts, specific findings
- Keep each LOG line under 80 characters where possible
- If a step is skipped, LOG why: `LOG: [P3.1] Linter: skipped — no linter configured`

---

## Quick Mode Self-Verification

Quick mode uses a compressed version:

```
LOG: [Q1] Reading SearchPage.jsx — confirm color change needed
ANNOUNCE: "Quick fix: Update button color in SearchPage."

LOG: [Q2] Changed background-color in SearchPage.css line 42
ANNOUNCE: "Change applied."

LOG: [Q3] ESLint: pass. 4 existing tests pass.
ANNOUNCE: "Verified. Tests pass."

LOG: [Q4] Self-check: 4/4 steps done ✅
[Summary presented, waiting for user]
```
