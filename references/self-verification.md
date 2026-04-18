# Self-Verification — Critical Outcomes

Loaded at the Ready Gate for Standard and Full mode. Quick mode verifies inline.

This file is the second verification layer. The first is `scripts/verify-pipeline.sh`, which checks real repo state. If the script and this self-check disagree, the script wins.

---

## How To Use This File

Ask one question for each outcome: does the evidence exist right now?

- If yes, mark it complete.
- If no, either fix the gap or report it.
- If the outcome is marked **BLOCK**, do not ship until it is resolved.

Keep the self-check short. Focus on whether the change is actually shippable, not whether every micro-step was narrated.

---

## Quick Mode Inline Check

Quick mode does not need this file unless the agent wants it.

1. The file was read before editing.
2. The change is present in the codebase.
3. Existing style and conventions were preserved.
4. Available checks were run, or the lack of tooling was stated.

---

## Critical Outcomes

| # | Outcome | Evidence | Blocked if missing? |
|---|---|---|---|
| 1 | Scope is clear | Brief summary includes acceptance criteria, source of truth, and relevant edge cases | No, warn |
| 2 | TDD happened or was concretely blocked | Failing reproducer exists before the fix, or the summary states a specific blocker | **YES for structural, behavioral, and security work when a harness exists** |
| 3 | Single source of truth and contract safety were preserved | No duplicate schema, validator, config, or public contract drift without explicit justification | **YES if the change introduces parallel truth or breaks callers** |
| 4 | Fix-Guard-Test-Verify was evidenced | Structural and security findings have a real fix, a guardrail, tests, and a root-cause scan or explicit local-only justification | **YES for structural and security work** |
| 5 | Tests are meaningful and passing | Test output passes, changed tests are not tautological, and edge or negative coverage exists when relevant | **YES for structural and security work** |
| 6 | Edge cases are closed | Relevant boundaries are tested, guarded, impossible by construction, or explicitly deferred as unresolved risk | **YES for structural and security work** |
| 7 | Security review ran when required | Standard and Full mode performed the security pass; Full mode also loaded `references/deep-audit.md` | **YES for Standard and Full** |
| 8 | Script output and self-check agree | `verify-pipeline.sh` output is shown and any contradiction was resolved or escalated explicitly | **YES** |
| 9 | Limitations and human-review guidance are honest | Summary includes the AI-review limitation line and the high-risk human-review note when applicable | **YES** |
| 10 | Deploy approval is explicit | If deployment is requested, the user approved the detected target, environment, and command | **YES for deploys** |

---

## Ready Gate Report Format

Use this shape at the Ready Gate:

```markdown
## Verification

### Script Output
[paste raw verify-pipeline.sh output here]

### Critical Outcomes
✅ [list completed outcomes]
⚠️ [list warnings]
❌ [list blockers]

### Agreement
AGREE
or
CONTRADICTION — [describe mismatch, diagnosis, and action]

### Limitations
AI-assisted review — catches known patterns, not novel vulnerabilities.
[If high-risk:] HUMAN REVIEW RECOMMENDED: This change touches [domain].
```

If automatic cross-model review is unavailable, add the optional copyable prompt after the verification report.

---

## Severity Rules

| Missing outcome | Action |
|---|---|
| 2, 3, 4, 5, 6, 7, 8, 9 | **BLOCK** shipping until fixed or explicitly escalated where allowed |
| 10 | **BLOCK** deploy only |
| 1 | Warn, but do not block if the diff is otherwise clear |

If tooling is unavailable, say so plainly. Do not pretend the outcome exists.

---

## Cross-Model Review Prompt Spec

If no second model is available through the current agent or toolchain, generate a copyable prompt in a fenced code block that includes:

1. The full diff.
2. What was requested.
3. What was changed, tested, guarded, and already reviewed.
4. Six adversarial tasks:
  (1) inspect changed logic line by line,
  (2) find missed edge cases,
  (3) find security gaps,
  (4) judge test quality,
  (5) look for guardrail bypasses,
  (6) identify what should have changed but did not.
5. The output format: severity, file:line, issue, suggested fix.
