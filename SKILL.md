---
name: sdlc-autopilot
description: "SDLC workflow for AI coding agents — turns coding prompts into tested, guarded code with risk-based modes (Quick/Standard/Full), expert mode, Fix-Guard-Test-Verify, TDD bias, edge-case closure, SSOT, DRY-with-judgment, and honest AI-review limits. Use for bug fixes, features, refactors, security work, API changes, deployment changes, or audits."
license: MIT
---

# SDLC Autopilot

One rough prompt in. A safer implementation workflow out.

**Principles:** Risk first. Fix the root cause. Guard against recurrence. Prefer TDD when practical. Preserve the single source of truth. Stay DRY with judgment. Cover relevant edge cases before stopping. Respect project conventions. Never auto-deploy. Never overclaim what AI review can prove.

**Token policy:** Keep the core skill lean. Load reference files only when needed: `references/self-verification.md` at the Ready Gate, `references/deep-audit.md` in Full mode, and `references/deployment.md` only when deployment is requested.

---

## AI Review Limits

This workflow includes AI-assisted review. It is NOT a professional security audit, penetration test, or expert human review.

**AI review can catch:** known vulnerability patterns, obvious null/undefined bugs, common input-validation gaps, off-by-one mistakes, hardcoded secrets, and familiar unsafe APIs such as `eval` or `innerHTML`.

**AI review cannot reliably catch:** novel attack paths, business-logic flaws, subtle distributed race conditions, cryptographic mistakes, supply-chain issues, or system-level risks outside the loaded context.

**Required language:** never say "security audit passed" or "professionally audited". Always describe the result as "AI-assisted review". For auth, payments, PII, crypto, medical, or legal work, the final summary must include: "HUMAN REVIEW RECOMMENDED: This change touches [domain]."

---

## Fix-Guard-Test-Verify

This is the core of the skill. Apply it to the original request and to every structural, behavioral, or security issue discovered during verification. Cosmetic work stays proportional.

1. **Fix** the issue.
2. **Root cause:** explain why it happened. Search for the same pattern elsewhere. Read every candidate in context before changing it. Fix only confirmed matches with the same risk and no existing guard. Cap at 5 fixes; if more remain, triage by severity and report the rest as unresolved risk.
3. **Guard:** add the lightest effective protection for the bug class. Prefer this order: type/compiler rule, linter/static analysis, runtime assertion/invariant, targeted test, comment as a last resort.
4. **Test the guard:** the test set must prove the fix, prove the guardrail matters, and cover the relevant edge cases.
5. **Verify:** run the tests. If the fix fails its own checks, retry the loop. Maximum 3 retries per finding. If it still does not converge, stop and defer to the user. If a follow-on fix breaks unrelated existing tests, revert that follow-on fix and report it as deferred.

**Test quality rules:** every new or updated regression test should satisfy these unless the project tooling makes one impossible, in which case say why.

- **Inversion:** the test should fail on the pre-fix code.
- **Behavior over implementation:** assert outputs, side effects, or errors, not internal calls.
- **Negative coverage:** include at least one bad, boundary, or malformed-input case.
- **Minimal mocking:** mock only external I/O.

**Proportionality:**

- **Structural:** logic errors, data loss, security holes, race conditions, validation gaps. Use the full loop.
- **Behavioral:** wrong return values, missing error handling, incomplete boundary handling. Use the loop with a targeted root-cause scan or an explicit local-only justification.
- **Cosmetic:** naming, formatting, copy, low-risk DRY cleanup. Fix only unless Full mode requires a stronger guard.
- **Security findings:** always use the full loop.

---

## Engineering Standards

Standard and Full mode treat these as non-negotiable. Quick mode applies them proportionally.

1. **TDD bias:** if a failing reproducer is cheap and the harness exists, write it before the fix. If not, state the blocker and add the regression test immediately after the fix.
2. **Single source of truth:** extend the canonical schema, type, validator, config, helper, or contract instead of creating a parallel copy.
3. **DRY with judgment:** remove duplication that increases bug surface area. Do not abstract a one-off into a framework.
4. **Edge-case closure:** before stopping, account for the relevant boundaries: empty, null, undefined, malformed, unauthorized, timeout, retry, concurrency, backward compatibility, accessibility, and performance. Each relevant edge case must be tested, guarded, impossible by construction, or deferred as explicit unresolved risk. Deferred structural or security edge cases block shipping.
5. **Contract safety:** if an API, data model, event shape, schema, or config contract changes, update callers or provide a compatibility path.
6. **Smallest safe change:** fix the root cause without speculative refactors.

---

## Mode Selection

Choose the mode in this order.

| Condition | Mode |
|---|---|
| Security, auth, payments, PII, crypto, deployment, DB schema, shared-library contract changes | **Full** |
| User explicitly asks for `full`, `thorough`, `careful`, or equivalent | **Full** |
| Bug fixes, features, validation, refactors, performance work | **Standard** |
| Text, color, config, comments, docs, simple rename with no behavior impact | **Quick** |
| Ambiguous risk | **Standard** |

Words like `just` or `quickly` can bias low-risk work toward Quick mode, but never below the safe floor above.

### Expert Mode

If the user, repo instructions, or project guidance explicitly says `expert mode`, `power mode`, or `I know what I'm doing`, keep the same safety rules, Fix-Guard-Test-Verify loop, Ready Gate, and honest disclosure, but strip out optional ceremony. Do not skip TDD, edge-case closure, guardrails, security review, or verification. Expert mode is a presentation shortcut, not a safety downgrade.

State the selected mode when it is non-obvious, promoted from Quick, or elevated by risk.

---

## Quick Mode

Use this only for truly trivial, localized changes.

- Read the target file.
- Make the smallest safe change.
- Run lint/tests if available.
- Present a one-line summary with the verification result and the limitation note: `AI-reviewed, not human-audited.`
- Hard stop for user confirmation before commit, push, PR, or deploy.

**Promote immediately** to Standard or Full if the work expands beyond one file, changes behavior, needs tests, needs a guardrail, or touches a risky domain.

---

## Standard Mode

Use this 5-phase pipeline for most real work.

### Phase 1: Understand

1. Clarify the request.
2. Explore only the relevant code, project rules, and installed skills.
3. Produce a brief implementation plan with acceptance criteria, root-cause hypothesis for bugs, canonical sources of truth, an edge-case matrix, and a test strategy.
4. If the request is still ambiguous after that, ask one focused question.

### Phase 2: Implement

1. If on `main` or `master`, warn and offer a branch. The user may explicitly override.
2. For structural, behavioral, and security work with an existing harness, prefer a failing targeted test first.
3. Make the change according to the plan and existing conventions.
4. Delegate to relevant installed skills for domain-specific best practices.
5. Keep scope tight. Note unrelated issues without changing them.

### Phase 3: Verify

1. Run linter, formatter, and type checker if available. Auto-fix up to 3 cycles.
2. Run existing tests. Fix failures caused by the change. Record unrelated pre-existing failures without claiming to fix them.
3. Apply Fix-Guard-Test-Verify to the original request.
4. Audit the full diff for correctness, security, performance, accessibility, and source-of-truth drift. Every real finding gets the loop with proportionality.
5. Review the edge-case matrix. Every relevant edge case must be closed or explicitly deferred as unresolved risk.
6. Run the full affected test scope again and confirm the guardrails still exist after all edits.

### Phase 4: Ready Gate

1. Run `scripts/verify-pipeline.sh standard` if shell access exists and show the raw output.
2. Load `references/self-verification.md` and complete the critical-outcomes check.
3. If the script and self-check disagree, say so explicitly, investigate, fix if possible, and rerun. The script is authoritative.
4. Produce a concise summary: what changed, tests added or updated, TDD status, edge cases covered, deferred risks, root-cause scan results, guardrails added, verification result, and the mandatory AI-review limitations line.
5. If another model is available through the current toolchain, run a structural adversarial review automatically. Otherwise generate the optional copyable cross-model review prompt from `references/self-verification.md`.
6. Hard stop for user confirmation.

### Phase 5: Ship

1. Stage, commit with a conventional message, and push the branch.
2. Create a PR if requested.
3. Update the changelog if the project uses one.
4. If deployment is requested, load `references/deployment.md`, show the detected platform, environment, and exact command, and wait for explicit approval. Default to preview or staging; production requires an explicit `prod` or `production` instruction.

---

## Full Mode

Full mode is Standard mode plus stricter controls.

- **Before implementing:** present the plan and wait for explicit approval.
- **During Verify:** load `references/deep-audit.md` and perform the deeper security pass. Add a convergence pass that re-checks every structural and security fix for guardrails and tests. If the main audit found zero additional issues, you may skip the extra convergence pass.
- **Guardrails:** executable guardrails are mandatory for structural and security findings unless no executable guard is viable and the reason is explicit.
- **Summary:** always include the human-review recommendation for high-risk domains.

---

## Dynamic Skill Delegation

This skill decides the workflow. Other installed skills provide domain-specific depth.

- Scan installed skills during Understand.
- When the work reaches a matching domain, read that skill and follow it.
- Keep this skill in control of risk, testing, verification, and disclosure.

---

## Safety Rules

- Never expose secrets in output, code, or commits.
- Never auto-deploy.
- Never silently continue past an unresolved verification contradiction.
- If you cannot find the bug, report what you searched and ask one focused question.
- In monorepos, scope work, scans, and tests to the affected packages first.
- In large repos, read only relevant files and use targeted searches for root-cause scans.
- If tooling is missing, do not abandon the workflow. Write logical tests, list the commands, and note the limitation.
- If the user says `stop` or `cancel`, revert only the changes from the current run when they can be isolated safely. If isolation is unclear, ask before any destructive cleanup.
- Project style rules outrank this skill for formatting and local conventions. This skill outranks default agent behavior for process, guardrails, and disclosure.

**Two-layer verification at Ready Gate:** (1) `scripts/verify-pipeline.sh <mode>` — deterministic filesystem checks, output shown RAW. (2) Agent self-assessment via self-verification.md (or inline for Quick). (3) Contradiction protocol — script is authoritative, disagreements stated and resolved. Quick mode runs script if shell available, falls back to inline 4-item check. Missing security outcomes block shipping. See self-verification.md for examples and full checklist.
