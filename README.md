# sdlc-autopilot

**Structured SDLC discipline for AI coding agents.** One messy prompt in → a stricter implementation workflow with testing, guardrails, review, and explicit limits.

```bash
npx skills add mrqureshi95/sdlc-autopilot
```

Works with **Claude Code · GitHub Copilot · Cursor · Windsurf · Codex · Cline · Roo · Amp** and [30+ other agents](https://skills.sh).

---

### What you get

- **Automatic risk-based pipeline** — Quick (trivial) · Standard (5 phases) · Full (deep review) · Expert mode overlay
- **Fix-Guard-Test-Verify loop** — every fix is guarded against recurrence, not just patched
- **Test quality enforcement** — inversion principle, negative cases, behavior-based assertions (no tautological tests)
- **AI-assisted review** — verification reviews the full diff for known patterns and common issues, with honest limitations (see [What this is NOT](#what-this-is-not))
- **Guardrail generation** — prevents the same class of bug from recurring
- **Root cause scanning** — finds the same pattern elsewhere, verifies each match in context before fixing (no blind grep-and-fix)
- **Two-layer verification** — external script + agent self-assessment, with contradiction protocol
- **Optional strict inversion gate** — prototype execution-based check for “would this test fail before the fix?”
- **Cross-model review** — automatic second-model review when available, otherwise a copyable adversarial prompt for independent verification
- **Machine-checkable eval harness** — artifact-based scoring path for agent runs against fixtures
- **Honest limitations disclosure** — every change summary states what AI review can and cannot catch
- **Zero config** — auto-detects your toolchain, test framework, and deploy target
- **Graceful degradation** — works even without tests, linters, or shell access

---

## The Problem

AI coding agents implement what you ask and stop. They don't self-audit, don't write tests unprompted, don't check for regressions, don't verify API contracts, and critically — they don't prevent bug recurrence. CI/CD catches problems after push — too late. You end up with the same class of bug reappearing across your codebase.

## The Solution

SDLC Autopilot transforms any rough prompt into a risk-based workflow for implementation, testing, review, and verification. It raises the floor on agent behavior by forcing structured checks, guardrails, and explicit disclosure of what was and was not verified. A button color change gets light treatment. An auth overhaul gets the heavy path.

## The Core Innovation: Fix-Guard-Test-Verify

This is what makes SDLC Autopilot different from everything else. Every issue found — the original request AND issues discovered during audit — goes through a closed loop:

```
ISSUE FOUND
    │
    ▼
1. FIX the issue
    │
    ▼
2. ROOT CAUSE: Why? Does the same pattern exist elsewhere? (grep)
   If found → fix those too (up to 5 occurrences)
    │
    ▼
3. GUARD: Prevent this CLASS of issue from recurring
   Priority: type constraint > linter rule > assertion > test > comment
    │
    ▼
4. TEST THE GUARD: Write tests that verify the fix AND the guardrail
    │
    ▼
5. VERIFY: Run tests. Pass → continue. Fail → loop back. Break others → revert.
```

**Nothing is "just patched."** Every non-trivial fix gets a guardrail and a test — making the same bug class harder to reintroduce.

## What This CAN Prove

- The repo can prove that a patch exists, tests were added or updated, and the verifier scripts were run.
- In strict mode, it can sometimes prove that at least one changed test fails on the base revision and passes now.
- It can prove that the agent produced specific artifacts and that those artifacts satisfy machine-checkable eval rules.

## What This CANNOT Prove

- It cannot prove full correctness of the code.
- It cannot prove absence of vulnerabilities.
- It cannot prove that every edge case in a real system has been found.
- It cannot replace expert human review for high-risk code.

## What This Is NOT

SDLC Autopilot uses AI-assisted code review — the same LLM that wrote the code reviews it. This is valuable (it catches known patterns, common vulnerabilities, and obvious mistakes) but it has real limitations:

- **It is NOT a professional security audit.** It cannot catch novel attack vectors, complex business logic flaws, or subtle cryptographic errors.
- **It is NOT a substitute for expert human review** on high-risk code (auth, payments, PII, crypto, medical, legal).
- **It is NOT penetration testing.** It pattern-matches against known vulnerability signatures — it doesn't probe your running system.

Every change summary includes a limitations disclosure. For high-risk domains, the pipeline adds a "⚠️ HUMAN REVIEW RECOMMENDED" notice. This keeps you honest about what you've actually verified.

**The value is real:** structured process, automated testing, guardrail generation, root cause scanning, and catching the 80% of issues that follow known patterns. But the last 20% — novel vulnerabilities, business logic, system-level concerns — requires human expertise.

## Security Review Note

This repository includes intentionally vulnerable example code under `evals/fixtures/` so the skill can be tested against real bug classes like SQL injection and XSS. That code is non-production test material.

- Do not deploy anything from `evals/fixtures/`.
- Expect repository-wide code scanners to flag those fixtures unless they are scoped or excluded appropriately.
- When reviewing the security posture of the skill itself, evaluate the root skill/docs/scripts separately from the intentionally insecure fixtures.

## Before / After

| | Before (vanilla agent) | After (SDLC Autopilot) |
|---|---|---|
| **Null crash** | Adds one null check | Adds null check + scans for same pattern (verifies each match in context) + fixes 3 confirmed locations + adds `assertDefined` utility + tests all 4 |
| **SQL injection** | Fixes one query | Fixes query + scans all queries (verifies each, skips false positives) + adds parameterized query wrapper + guardrail test + AI-assisted security review |
| **CSS overlap bug** | Fixes one element | Fixes element + finds same pattern elsewhere + adds CSS comment guardrail + regression test |
| **Test quality** | 5 tautological tests pass | Inversion-checked tests that fail on pre-fix code + negative cases + behavior assertions |
| **AI-assisted review** | None (not reviewed) | AI-assisted review in 2 passes, every structural finding gets the full loop + honest limitations disclosed |
| **Independent verification** | None | Cross-model review prompt generated — paste into a different AI for adversarial review |

---

## Installation

### All Agents (Recommended)
```bash
npx skills add mrqureshi95/sdlc-autopilot
```

This works with Claude Code, Cursor, GitHub Copilot, Windsurf, Codex, Cline, Roo, OpenCode, Amp, and 30+ other agents. The CLI auto-detects your installed agents.

### Install globally (available across all projects)
```bash
npx skills add mrqureshi95/sdlc-autopilot -g
```

### Install to specific agents
```bash
npx skills add mrqureshi95/sdlc-autopilot -a claude-code -a cursor -a github-copilot
```

### Manual Installation
If you prefer not to use the CLI, copy the `SKILL.md` file to your agent's skills directory:
- **Claude Code:** `.claude/skills/sdlc-autopilot/SKILL.md`
- **GitHub Copilot:** `.agents/skills/sdlc-autopilot/SKILL.md`
- **Cursor:** `.agents/skills/sdlc-autopilot/SKILL.md`
- **Windsurf:** `.windsurf/skills/sdlc-autopilot/SKILL.md`

---

## Usage

The skill auto-triggers on any coding task. Just describe what you want:

### Quick Mode (low risk)
> "change the error message from 'Not found' to 'Item not found'"

Result: ~60 seconds. Trivial changes (single value, one file) skip ceremony — just the change and a one-line summary. If the work stops being trivial, Quick mode promotes immediately.

### Standard Mode (medium risk — the default)
> "the search field gets hidden behind the keyboard on mobile"

Result: Full 5-phase pipeline. Implementation brief, TDD-biased implementation, Fix-Guard-Test-Verify, full-diff verification, and a lean ready gate.

### Full Mode (high risk)
> "the login endpoint might be vulnerable to SQL injection"

Result: Everything in standard + user checkpoint before implementation, deep security review, convergence on structural/security findings, and mandatory executable guardrails for high-risk work. Includes ⚠️ HUMAN REVIEW RECOMMENDED for high-risk domains.

### Override Mode
> "change the button text but do the full lifecycle please"

Result: User override respected. Full mode even for low-risk change.

### Expert Mode
> "fix the bug, expert mode, I know what I'm doing"

Result: Same safety gates, TDD bias, guardrails, edge-case closure, and verification. Less ceremony in how the agent presents the work.

---

## How It Works

```
User Prompt → Mode Selection (Quick / Standard / Full)
                     │
    ┌────────────────┼────────────────┐
    │                │                │
  Quick          Standard           Full
    trivial path    5 phases        5 + extras
    │                │                │
    ▼                ▼                ▼
 Read/Edit     1. Understand     Standard +
 Verify        2. Implement      User checkpoint
 Ready Gate ⛔ 3. Verify         Deep security review
 Ship          4. Ready Gate ⛔  Convergence pass
                             5. Ship          Stronger guardrails
```

**Token budget (skill instruction overhead only):**
- SKILL.md: lean core loaded on activation for all modes
- Standard add-on: slim critical-outcomes checklist at the Ready Gate
- Full add-on: deep-audit.md for the deeper security pass
- Deploy add-on: deployment.md only when deployment is requested
- Quick mode: core skill only — verifies inline, no extra files loaded

Total pipeline cost depends on your codebase size and number of files read.

---

## Architecture

```
sdlc-autopilot/
├── SKILL.md              # Lean core pipeline
├── GUIDANCE.md           # Companion doc with diagrams and explanations
├── references/
│   ├── deep-audit.md     # Security checklist + guardrail patterns (full mode only)
│   ├── deployment.md     # All deploy targets in one file (deploy phase only)
│   └── self-verification.md  # Critical-outcomes checklist (ready gate)
├── scripts/
│   ├── detect-toolchain.sh  # Auto-detect project tools (optional)
│   ├── run-gates.sh         # Lint + typecheck + test runner (optional)
│   ├── run-agent-evals.py   # Machine-checkable harness for agent run artifacts
│   ├── verify-inversion.sh  # Prototype execution-based inversion verifier
│   ├── verify-pipeline.sh   # External pipeline verification (Ready Gate)
│   └── run-evals.sh         # Validate fixture structure (dev only)
├── evals/
│   ├── evals.json        # 23 evaluation scenarios (manual verification)
│   └── fixtures/         # Minimal project fixtures for each test
├── examples/
│   ├── quick-change-walkthrough.md
│   ├── bug-fix-walkthrough.md
│   └── feature-walkthrough.md
├── README.md
├── LICENSE.txt           # MIT
├── CONTRIBUTING.md
└── CHANGELOG.md
```

---

## Agent Compatibility

This skill works with any agent that supports the Agent Skills specification — but the experience varies by agent mode:

| Mode | Agents | What You Get |
|---|---|---|
| **Full benefit (agentic)** | Claude Code, Copilot agent mode, Cursor (with terminal), Codex, Cline, Roo | All phases work including automated linting, test execution, git operations, deployment |
| **Partial benefit (chat)** | Copilot chat, Cursor chat-only, Windsurf chat | Planning, implementation, verification, and guard phases work; automated gates are written out as commands for you to run manually |

**Agent cooperation:** This skill's phases are outcomes to achieve, not rigid ceremonies. If your agent already handles branching, testing, or committing natively, use the agent's mechanics — the skill adds the fix-guard-test-verify loop and structured audit on top, not duplicate infrastructure. When a phase's outcome is already satisfied by the agent's built-in behavior, the agent notes it and moves on.

The pipeline degrades gracefully. Even in chat-only mode, you get the structured SDLC process, guardrail generation, and verification flow — you just run the terminal commands yourself.

---

## FAQ

**How much does this cost in tokens?**
The core skill is intentionally lean. Reference files are loaded only when needed: self-verification.md at the Ready Gate, deep-audit.md in Full mode, and deployment.md only for deploy work. Quick mode stays on the core skill alone. The verification script (`verify-pipeline.sh`) runs externally and doesn't consume context tokens beyond its output.

**How do I know the agent actually followed the pipeline?**
The skill uses two-layer verification. First, `scripts/verify-pipeline.sh` checks real filesystem state — changes exist, tests pass, coverage evidence is present when the project exposes it, executable guardrail signals exist, changed tests have a meaningful assertion count, and no secrets or dangerous patterns were added. This output is deterministic and shown to you RAW. Second, the agent walks a short critical-outcomes checklist from `self-verification.md`. If the script and self-assessment disagree, the contradiction is stated explicitly and the script wins. Missing security checks, missing guardrails, or missing limitation disclosure block shipping.

**Can it verify the inversion principle automatically?**
Partially. The repo now includes `scripts/verify-inversion.sh`, a prototype that runs changed tests on the current worktree and a temporary base worktree to check whether at least one changed test fails on pre-fix code and passes now. It currently supports targeted Jest, Vitest, and pytest runs. It is intentionally marked as a prototype because import/collection failures can still make results inconclusive.

If you want the main verifier to enforce this stricter gate, run `verify-pipeline.sh` with `SDLC_STRICT_INVERSION=1`. You can also set `SDLC_INVERSION_BASE_REF=<git-ref>` to override the base revision used by the prototype.

**What happens if the script and the agent disagree?**
This is the contradiction protocol. The agent must state the mismatch (e.g., "Script found 0 test files, but I reported writing 3 tests"), diagnose the cause (e.g., tests written but not saved), fix it, and re-run the script. If it can't fix the discrepancy, it shows you both outputs and lets you decide. The agent can never silently proceed past a contradiction.

**What languages does it support?**
Any. The pipeline is language-agnostic. The scripts auto-detect toolchains for JS/TS, Python, Go, Rust, Ruby, and Java. For others, the pipeline still works — it just skips automated gates.

**Can I customize the AI-assisted review?**
Yes. Edit `references/deep-audit.md` to add security patterns, guardrail templates, or domain-specific checks. See [CONTRIBUTING.md](CONTRIBUTING.md).

**Is the AI review as good as a human security audit?**
No — and the skill is honest about this. Every change summary includes a limitations disclosure. AI review catches known patterns (SQL injection, XSS, missing auth checks, hardcoded secrets) but cannot catch novel attack vectors, business logic flaws, or complex cryptographic errors. For high-risk code (auth, payments, PII), the pipeline adds a "⚠️ HUMAN REVIEW RECOMMENDED" notice. Think of it as a thorough first pass that catches the common 80%, not a replacement for expert review on the critical 20%.

**What is cross-model review?**
At the Ready Gate, the pipeline tries to run a second-model adversarial review automatically if the current toolchain makes that possible. If not, it generates a self-contained prompt you can paste into a **different AI model**. The prompt includes the full diff, what was done, what was already tested/guarded, and six structured adversarial review tasks. Different models have different blind spots, so a second opinion from a different model catches things the first one missed. It's optional in Standard mode and strongly recommended for Full/HIGH-RISK changes.

**What if my project has no tests or linter?**
The pipeline degrades gracefully. Tests are still written (in logical format for the language). Gates are skipped. A test framework suggestion is provided but doesn't block the pipeline.

**Can the eval suite be machine-checked now?**
Partially. The repo now includes `scripts/run-agent-evals.py`, which evaluates agent-run artifacts (`meta.json`, `patch.diff`, optional `transcript.md`) against fixtures in a temporary git workspace. It applies the patch, runs `verify-pipeline.sh`, and scores optional `machine_checks` declared in `evals/evals.json`. This is still not full end-to-end agent automation, but it is a real step beyond fixture-structure-only validation.

**Does it work with monorepos?**
Yes. It auto-detects monorepo structures (`packages/`, `apps/`, `pnpm-workspace.yaml`, `lerna.json`) and scopes tests and root cause scans to affected packages only.

**Does it auto-deploy?**
Never. Even after "ship it" / "deploy", the agent shows the detected platform, environment, and exact command — then waits for confirmation before running anything. Defaults to preview/staging; production requires you to explicitly say "prod." Auto-detection can misidentify targets (e.g., a Dockerfile for local dev), so the confirmation gate prevents misdeployments.

**Can it create PRs?**
Yes. Say "create PR" at the ready gate and it creates a PR with the change summary as the description using `gh`.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding evals, extending the audit, and submitting PRs.

If you find this useful, a ⭐ on the repo helps others discover it.

---

## License

[MIT](LICENSE.txt)
