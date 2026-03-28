# sdlc-autopilot

**Full software development lifecycle execution for AI coding agents.** One messy prompt in, deploy-ready tested and guarded code out.

---

## The Problem

AI coding agents implement what you ask and stop. They don't self-audit, don't write tests unprompted, don't check for regressions, don't verify API contracts, and critically — they don't prevent bug recurrence. CI/CD catches problems after push — too late. You end up with the same class of bug reappearing across your codebase.

## The Solution

SDLC Autopilot transforms any rough prompt into a full lifecycle execution — tailored to the change's risk. It catches issues before commit, fixes them, guards against them, tests the guards, and verifies everything works. A button color change gets 60 seconds. An auth overhaul gets the full treatment.

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

**Nothing is "just patched."** Every fix is permanent.

## Before / After

| | Before (vanilla agent) | After (SDLC Autopilot) |
|---|---|---|
| **Null crash** | Adds one null check | Adds null check + finds 3 more locations with same pattern + adds `assertDefined` utility + tests all 4 |
| **SQL injection** | Fixes one query | Fixes query + scans all queries + adds parameterized query wrapper + guardrail test + security audit |
| **CSS overlap bug** | Fixes one element | Fixes element + finds same pattern elsewhere + adds CSS comment guardrail + regression test |
| **Audit findings** | None (not audited) | Self-audits in 2 passes, every structural finding gets the full loop |

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

Result: ~60 seconds. Change made, tests pass, summary presented.

### Standard Mode (medium risk — the default)
> "the search field gets hidden behind the keyboard on mobile"

Result: Full 7-phase pipeline. Implementation brief, fix with guardrail, tests, 2-pass audit, regression check, change summary with ready gate.

### Full Mode (high risk)
> "the login endpoint might be vulnerable to SQL injection"

Result: Everything in standard + user checkpoint before implementation, 3-pass audit with convergence, security deep dive (OWASP Top 10), mandatory guardrails on all findings.

### Override Mode
> "change the button text but do the full lifecycle please"

Result: User override respected. Full mode even for low-risk change.

---

## How It Works

```
User Prompt → Mode Selection (Quick / Standard / Full)
                     │
    ┌────────────────┼────────────────┐
    │                │                │
  Quick          Standard           Full
  4 phases       7 phases        7 + extras
    │                │                │
    ▼                ▼                ▼
 Understand    1. Understand     Standard +
 Implement     2. Implement      User checkpoint
 Verify        3. Gate & Test    3-pass audit
 Ship ⛔       4. Audit          Security deep dive
               5. Regression     Mandatory guardrails
               6. Ready Gate ⛔
               7. Ship
```

**Token budget (skill instruction overhead only):**
- SKILL.md: ~4,900 tokens (loaded on activation for all modes)
- Standard add-on: ~2,400 tokens (self-verification.md at Ready Gate)
- Full add-on: ~2,100 tokens (deep-audit.md) + ~2,400 tokens (self-verification.md)
- Deploy add-on: ~2,100 tokens (deployment.md, loaded once)
- Quick mode: SKILL.md only — verifies inline, no extra files loaded

Total pipeline cost depends on your codebase size and number of files read.

---

## Architecture

```
sdlc-autopilot/
├── SKILL.md              # Core pipeline (~318 lines)
├── GUIDANCE.md           # Companion doc with diagrams and explanations
├── references/
│   ├── deep-audit.md     # Security checklist + guardrail patterns (full mode only)
│   ├── deployment.md     # All deploy targets in one file (deploy phase only)
│   └── self-verification.md  # Pipeline compliance ledger (ready gate)
├── scripts/
│   ├── detect-toolchain.sh  # Auto-detect project tools (optional)
│   ├── run-gates.sh         # Lint + typecheck + test runner (optional)
│   └── run-evals.sh         # Validate eval fixtures (dev only)
├── evals/
│   ├── evals.json        # 16 eval test cases
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
| **Partial benefit (chat)** | Copilot chat, Cursor chat-only, Windsurf chat | Planning, implementation, audit, and guard phases work; automated gates are written out as commands for you to run manually |

The pipeline degrades gracefully. Even in chat-only mode, you get the structured SDLC process, guardrail generation, and audit passes — you just run the terminal commands yourself.

---

## FAQ

**How much does this cost in tokens?**
SKILL.md (~4,900 tokens) is loaded on activation. Reference files are loaded only when needed: self-verification.md (~2,400 tokens) at the Standard/Full Ready Gate, deep-audit.md (~2,100 tokens) in Full mode, deployment.md (~2,100 tokens) at deploy time. Quick mode loads only SKILL.md and verifies inline. Total pipeline cost depends on your codebase — reading files, running tools, and generating code are additional.

**How do I know the agent actually followed the pipeline?**
The skill has built-in self-verification. Throughout execution, the agent emits `LOG:` lines with concrete details (file names, counts, findings) so you can see what's happening in real time. At the Ready Gate, it loads `self-verification.md` and checks a compliance ledger — verifying every required step was completed. The change summary includes a "Pipeline Compliance: N/M steps" report. Missing security checks block shipping.

**What languages does it support?**
Any. The pipeline is language-agnostic. The scripts auto-detect toolchains for JS/TS, Python, Go, Rust, Ruby, and Java. For others, the pipeline still works — it just skips automated gates.

**Can I customize the audit?**
Yes. Edit `references/deep-audit.md` to add security patterns, guardrail templates, or domain-specific checks. See [CONTRIBUTING.md](CONTRIBUTING.md).

**What if my project has no tests or linter?**
The pipeline degrades gracefully. Tests are still written (in logical format for the language). Gates are skipped. A test framework suggestion is provided but doesn't block the pipeline.

**Does it work with monorepos?**
Yes. It auto-detects monorepo structures (`packages/`, `apps/`, `pnpm-workspace.yaml`, `lerna.json`) and scopes tests and root cause scans to affected packages only.

**Does it auto-deploy?**
Never. It always stops at the ready gate (Phase 6) and waits for explicit user approval. Deployment only happens on "ship it" / "deploy" / "push".

**Can it create PRs?**
Yes. Say "create PR" at the ready gate and it creates a PR with the change summary as the description using `gh`.

---

## License

[MIT](LICENSE.txt)
