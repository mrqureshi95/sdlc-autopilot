# SDLC Autopilot — Guidance

## What It Is

SDLC Autopilot is an agent skill that forces useful engineering discipline without turning every change into ceremony. The live skill is now built around a leaner model:

- Quick mode for truly trivial edits.
- Standard mode as a 5-phase workflow.
- Full mode for high-risk work.
- Expert mode as an overlay that removes presentation overhead without weakening safeguards.
# SDLC Autopilot — Guidance

## What It Is

SDLC Autopilot is an agent skill that forces useful engineering discipline without turning every change into ceremony. The live skill is now built around a leaner model:

- Quick mode for truly trivial edits.
- Standard mode as a 5-phase workflow.
- Full mode for high-risk work.
- Expert mode as an overlay that removes presentation overhead without weakening safeguards.

The point is not to make the agent narrate process. The point is to make the agent produce better code: tests that matter, guardrails that reduce recurrence, honest limitations, and a ready gate that surfaces real evidence.

---

## Activation Model

The skill is triggered by its description, which is intentionally broad enough to match normal coding requests: bug fixes, features, refactors, security work, API changes, deployment changes, and audits.

Once triggered, the agent should load only what it needs:

- [SKILL.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/SKILL.md) for the main workflow.
- [references/self-verification.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/references/self-verification.md) only at the Ready Gate.
- [references/deep-audit.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/references/deep-audit.md) only in Full mode.
- [references/deployment.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/references/deployment.md) only for deploy work.

This keeps the workflow useful for large codebases and vibe-coding sessions where instruction bloat can crowd out the actual repo context.

---

## Core Loop

The real differentiator is Fix-Guard-Test-Verify.

1. Fix the issue.
2. Scan for the same root-cause pattern elsewhere and verify each match in context before changing it.
3. Add the lightest effective guardrail.
4. Write tests that prove the fix and the guardrail matter.
5. Verify the result.

Key properties of the current design:

- Root-cause scans are verify-before-fix, not blind grep-and-rewrite.
- Each finding has a hard retry cap of 3 loops.
- Structural and security findings always get the full loop.
- Behavioral work gets the loop unless the agent can explicitly justify that the issue is local-only.
- Cosmetic work stays proportional.

This is the part of the skill that should stay opinionated. It is the actual quality lever.

---

## Test Quality Standards

The skill now treats test quality as a first-class concern rather than a byproduct.

Every meaningful regression or guardrail test should satisfy:

1. Inversion: it would fail on the pre-fix code.
2. Behavior over implementation: it asserts outputs, side effects, or errors.
3. Negative coverage: it exercises bad, malformed, or boundary input when relevant.
4. Minimal mocking: only external I/O gets mocked.

That is important for vibe coders because green tests are otherwise easy to fake. A shallow test suite creates false confidence faster than no tests at all.

---

## Engineering Standards

These are deliberately preserved in the live skill and remain non-negotiable for Standard and Full mode:

- TDD bias.
- Single source of truth.
- DRY with judgment.
- Edge-case closure.
- Contract safety.
- Smallest safe change.

The edge-case closure rule is especially important. The agent should leave each relevant edge case in one of four states only: tested, guarded, impossible by construction, or explicitly deferred as unresolved risk. Structural and security deferrals block shipping.

---

## Modes

### Quick

Quick mode is for one-file, non-behavioral edits. It reads the file, makes the change, runs available checks, and stops at user confirmation. The moment the work requires behavior changes, tests, or guardrails, it must promote.

### Standard

Standard mode is now 5 phases:

1. Understand
2. Implement
3. Verify
4. Ready Gate
5. Ship

The crucial change is that verification is unified. The agent no longer needs separate ritual phases for “gate and test”, “audit”, and “regression”. Those are now one coherent verify phase.

### Full

Full mode keeps Standard mode but adds:

- User approval before implementation.
- Deeper security review via [references/deep-audit.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/references/deep-audit.md).
- A convergence pass on structural and security changes.
- Stronger executable guardrail expectations.

### Expert Mode

Expert mode does not weaken the workflow. It simply removes optional ceremony when the user or repo guidance explicitly asks for it. The agent still owes TDD bias, guardrails, edge-case closure, verification, and honest disclosure.

---

## AI Review Limits

The skill is intentionally explicit about what AI review can and cannot do.

AI review is good at:

- Known vulnerability patterns.
- Null/undefined and off-by-one mistakes.
- Obvious validation gaps.
- Familiar unsafe APIs.

AI review is not proof of:

- Full correctness.
- Absence of vulnerabilities.
- Novel exploit resistance.
- Subtle business-logic soundness.
- System-wide safety.

That is why the live skill now insists on limitation disclosure in the final summary and a human-review recommendation for high-risk domains.

---

## Verification Model

The current repo uses two verification layers.

### Layer 1: External Script

[scripts/verify-pipeline.sh](/Users/muhammadqureshi/Projects/sdlc-autopilot/scripts/verify-pipeline.sh) checks repo evidence, not agent narration.

For Standard and Full mode it looks for:

- A real diff.
- Test-file updates when source changes exist.
- Passing tests.
- Coverage evidence when the project exposes coverage artifacts.
- Executable guardrail signals.
- Meaningful assertion counts in changed tests.
- No newly introduced secrets, dangerous patterns, or suppression markers.

In Full mode it also looks for security-specific guardrail signals.

### Layer 2: Critical Outcomes

[references/self-verification.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/references/self-verification.md) is now intentionally short. It focuses on 10 critical outcomes rather than a long ledger. That makes it more likely the agent will use it honestly instead of rubber-stamping a giant checklist.

### Contradictions

If the script and self-check disagree, the script wins. The agent must state the contradiction, diagnose it, try to fix it, and rerun verification. Silent disagreement is not allowed.

---

## Cross-Model Review

Cross-model review is now structural, not mandatory theater.

- If the current toolchain can invoke another model, the agent should use it.
- If it cannot, the agent should generate a copyable adversarial review prompt.
- In Standard mode it is recommended.
- In Full or high-risk work it is strongly recommended.

This makes the feature useful without pretending every environment supports automated multi-model orchestration.

---

## Agent Cooperation

The skill should cooperate with the agent’s native strengths.

- If the agent already manages branches, tests, or commits well, use those mechanics.
- SDLC Autopilot adds process discipline, not duplicated plumbing.
- The live skill now explicitly treats phases as outcomes, not rituals.

That matters for vibe coders because the workflow should feel like a safety rail, not a second product layered on top of the editor.

---

## Deployment Safety

Deployment remains gated.

- Never auto-deploy.
- Always show detected target, environment, and exact command.
- Default to preview or staging.
- Require an explicit `prod` or `production` instruction for production deploys.

This is unchanged in spirit, but it now aligns cleanly with the leaner 5-phase model.

---

## Graceful Degradation

The workflow should still function when tools are missing.

- No shell: write the commands the user should run.
- No test runner: write logical tests anyway.
- No linter or type checker: skip the automation, not the reasoning.
- No git: skip branch and commit mechanics, not verification.

The skill should never pretend evidence exists when tooling is absent. It should say what it could not verify.

---

## Evaluation Philosophy

The evaluation suite is now outcome-focused.

[evals/evals.json](/Users/muhammadqureshi/Projects/sdlc-autopilot/evals/evals.json) should answer questions like:

- Did the bug actually get fixed?
- Was there a guardrail?
- Did tests meaningfully cover the failure mode?
- Was the risky edge case surfaced or closed?

It should not mainly answer questions like:

- Did the agent emit the right ceremonial phase log?
- Did it say “audit pass 2” out loud?

That shift is important if the skill is supposed to stay valuable to people using agents pragmatically rather than performing process compliance.

---

## Repo Map

- [SKILL.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/SKILL.md): live workflow.
- [references/self-verification.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/references/self-verification.md): critical outcomes.
- [references/deep-audit.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/references/deep-audit.md): deep security review prompts and patterns.
- [references/deployment.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/references/deployment.md): deploy gating.
- [scripts/verify-pipeline.sh](/Users/muhammadqureshi/Projects/sdlc-autopilot/scripts/verify-pipeline.sh): external evidence checks.
- [scripts/run-agent-evals.py](/Users/muhammadqureshi/Projects/sdlc-autopilot/scripts/run-agent-evals.py): artifact-based eval harness.
- [evals/evals.json](/Users/muhammadqureshi/Projects/sdlc-autopilot/evals/evals.json): manual scenarios and optional machine checks.
- [examples/quick-change-walkthrough.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/examples/quick-change-walkthrough.md), [examples/bug-fix-walkthrough.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/examples/bug-fix-walkthrough.md), [examples/feature-walkthrough.md](/Users/muhammadqureshi/Projects/sdlc-autopilot/examples/feature-walkthrough.md): aligned walkthroughs.
