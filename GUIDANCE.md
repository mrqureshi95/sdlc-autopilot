# SDLC Autopilot — Guidance Document

## What Is It?

sdlc-autopilot is an **Agent Skill** — a set of instructions that AI coding agents (GitHub Copilot, Cursor, Claude Code, Windsurf, etc.) load to change how they handle coding tasks. Instead of the agent just making a code change and stopping, this skill forces it through a full software development lifecycle: understand → plan → implement → test → audit → guard → ship.

The user types one messy sentence like *"the search page crashes when you press enter"* — and the agent delivers a tested, audited, guarded fix with a conventional commit, ready to deploy.

---

## How It Gets Activated

```mermaid
flowchart LR
    A["User installs skill<br/><code>npx skills add mrqureshi95/sdlc-autopilot</code>"] --> B["Agent starts up"]
    B --> C["Agent loads name + description<br/>of ALL installed skills"]
    C --> D["User sends a coding prompt"]
    D --> E{"Does any skill's<br/>description match?"}
    E -->|"YES — sdlc-autopilot's description<br/>matches virtually ALL coding tasks"| F["Agent reads SKILL.md<br/>(~305 lines of instructions)"]
    E -->|NO| G["Agent uses default behavior"]
    F --> H["Pipeline begins"]
```

The key is the **description** field in the YAML frontmatter. It's written to match every possible coding task: *"bug fixes, features, refactors, improvements, performance, security fixes, API changes, UI changes, database changes..."* — so any coding prompt triggers it.

The agent only loads the full SKILL.md when triggered. This is called **progressive disclosure** — name+description are always in context (~574 chars), but the full ~305-line instruction set is loaded on-demand.

---

## The Core Innovation: Fix-Guard-Test-Verify Loop

This is what separates this skill from a basic "make the change" workflow. Every issue — the original request AND anything found during audit — goes through this loop:

```mermaid
flowchart TD
    A["🔧 FIX<br/>Apply the code change"] --> B["🔍 ROOT CAUSE<br/>Why did this happen?<br/>Grep for same pattern elsewhere<br/>Fix up to 5 occurrences"]
    B --> C["🛡️ GUARD<br/>Prevent this CLASS of issue<br/>from recurring"]
    C --> D["🧪 TEST THE GUARD<br/>Write tests that verify:<br/>• Fix works<br/>• Guard catches recurrence<br/>• Edge cases covered"]
    D --> E["✅ VERIFY<br/>Run tests"]
    E -->|PASS| F["Continue"]
    E -->|FAIL| A
    E -->|"Breaks existing tests<br/>(CIRCUIT BREAKER)"| G["⚡ REVERT<br/>Note as deferred"]
```

### Guardrail Priority

Use the FIRST viable option (lightest effective):

1. **Type/compiler enforcement** — caught at build time
2. **Linter/static analysis rule** — caught before tests
3. **Runtime assertion/invariant** — caught at test/runtime
4. **Targeted test** — caught during test suite
5. **Code comment at danger point** — caught during review

### Proportionality — Effort Scales With Severity

```mermaid
flowchart LR
    S["STRUCTURAL<br/><i>logic error, security hole,<br/>race condition</i>"] -->|"Full loop"| FL["Fix + Root Cause +<br/>Guard + Test + Verify"]
    B["BEHAVIORAL<br/><i>missing error handling,<br/>wrong return value</i>"] -->|"Partial loop"| PL["Fix + Guard +<br/>Test + Verify"]
    C["COSMETIC<br/><i>naming, formatting,<br/>minor DRY</i>"] -->|"Quick only"| QF["Fix only<br/><i>(+ comment in Full mode)</i>"]
```

**Security findings ALWAYS get the full loop — no exceptions.**

---

## Mode Selection

The skill picks one of 3 modes based on risk + user language:

```mermaid
flowchart TD
    P["User Prompt"] --> R{"Risk Classification"}
    R -->|"LOW<br/>text, color, config,<br/>comments, docs"| Q["⚡ Quick Mode<br/>4 phases"]
    R -->|"MEDIUM<br/>bug fixes, new components,<br/>validation, refactors"| S["🔧 Standard Mode<br/>7 phases (default)"]
    R -->|"HIGH<br/>auth, payments, PII,<br/>API, DB schema, security"| F["🔒 Full Mode<br/>7 phases + extras"]

    P --> L{"User Language"}
    L -->|"'just', 'quick', 'simple'"| QB["Bias toward Quick"]
    L -->|"‘careful’, ‘thorough’, ‘full’,<br/>‘full pipeline’, ‘full audit’, ‘full sdlc’"| FB["Force Full mode"]
    L -->|"No signal"| RB["Use risk classification"]

    F -.->|"⚠️ HARD RULE"| HR["HIGH risk can NEVER<br/>be Quick mode, even<br/>if user asks"]
    FB -.->|"✅ ALWAYS ALLOWED"| HR2["User can FORCE Full mode<br/>on ANY risk level"]
```

### Risk Classification Table

| Risk Level | Examples | Mode |
|---|---|---|
| **LOW** | Text/copy, color/style, config values, comments, simple renames, docs-only | Quick |
| **MEDIUM** | Bug fixes, new UI components, new functions, form fields, validation, behavior-preserving refactors | Standard |
| **HIGH** | Auth/authz, payments, PII/data handling, API changes, DB schema, shared libraries, security fixes, deployment config, env vars, multi-service | Full |

---

## The Full Pipeline (Standard Mode — 7 Phases)

```mermaid
flowchart TD
    subgraph P1["PHASE 1: UNDERSTAND & PLAN"]
        P1a["Parse intent: bug/feature/refactor/perf"] --> P1b["Scan codebase: file tree, grep, read ~10 files"]
        P1b --> P1c["Check for project rules<br/>.cursorrules, CONTRIBUTING.md, .editorconfig"]
        P1c --> P1d["Scan installed skills for delegation"]
        P1d --> P1e["Generate Implementation Brief:<br/>• Problem statement<br/>• Root cause hypothesis<br/>• Acceptance criteria (3-5)<br/>• Files to change<br/>• Skills to delegate to"]
        P1e --> P1f["Plan steps + test strategy"]
    end

    subgraph P2["PHASE 2: IMPLEMENT"]
        P2a["Git branch check: on main/master?<br/>→ Warn user, offer override<br/>Otherwise → stay on current branch"] --> P2b["Execute plan step-by-step"]
        P2b --> P2c["Delegate to installed skills<br/>for domain-specific work"]
        P2c --> P2d["Follow project conventions"]
    end

    subgraph P3["PHASE 3: GATE & TEST"]
        P3a["Run linter → auto-fix"] --> P3b["Run formatter → auto-fix"]
        P3b --> P3c["Run type checker → fix errors"]
        P3c --> P3d["Run existing test suite"]
        P3d --> P3e["Apply Fix-Guard-Test-Verify loop<br/>to original request"]
        P3e --> P3f["Write new tests:<br/>regression + guardrail + edge cases"]
        P3f --> P3g["Run ALL tests"]
    end

    subgraph P4["PHASE 4: AUDIT (2 passes)"]
        P4a["Pass 1: Correctness CHECKLIST<br/>• Each acceptance criterion met?<br/>• Off-by-one errors?<br/>• Null/undefined access?<br/>• Race conditions?<br/>• Error handling on failure paths?"] --> P4b["Each finding →<br/>Fix-Guard-Test-Verify loop"]
        P4b --> P4c["Run tests after pass 1"]
        P4c --> P4d["Pass 2: Security & Quality CHECKLIST<br/>• Input validation?<br/>• Injection risks (SQL, XSS)?<br/>• Auth on new endpoints?<br/>• Secrets exposed?"]
        P4d --> P4e["Each finding →<br/>Fix-Guard-Test-Verify loop"]
        P4e --> P4f["Run tests after pass 2"]
    end

    subgraph P5["PHASE 5: REGRESSION & FINAL"]
        P5a["Run FULL test suite"] --> P5b["Fix regressions with guard loop"]
        P5b --> P5c["Verify wiring: imports, routes, APIs"]
        P5c --> P5d["Guardrail completeness check:<br/>Every fix has guard + test?"]
        P5d --> P5e["Update docs if affected"]
    end

    subgraph P6["PHASE 6: READY GATE"]
        P6a["Generate change summary:<br/>• What changed<br/>• Files list<br/>• Test counts<br/>• Audit findings<br/>• Guardrails added<br/>• Commit message"]
        P6a --> P6b["⛔ HARD STOP<br/>Wait for user"]
    end

    subgraph P7["PHASE 7: SHIP"]
        P7a["Git: commit + push branch"] --> P7b{"Create PR?"}
        P7b -->|YES| P7c["gh pr create with<br/>structured PR template"]
        P7b -->|NO| P7c2["Update CHANGELOG<br/>if project has one"]
        P7c -->  P7c2
        P7c2 --> P7d{"Deploy?"}
        P7d -->|YES| P7e["Auto-detect platform<br/>→ deploy"]
        P7e --> P7f["Health check"]
    end

    P1 --> P2 --> P3 --> P4 --> P5 --> P6
    P6b -->|"'ship it' / 'push'"| P7
    P6b -->|"'change X'"| P2
    P6b -->|"'cancel'"| DISCARD["Discard branch"]
```

---

## Quick Mode vs Standard vs Full

```mermaid
flowchart LR
    subgraph Quick["⚡ Quick (4 phases)"]
        QP1["Understand"] --> QP2["Implement<br/><i>lightweight guard loop</i>"]
        QP2 --> QP3["Verify<br/><i>lint + existing tests</i>"]
        QP3 --> QP4["Ship"]
    end

    subgraph Standard["🔧 Standard (7 phases)"]
        SP1["Understand & Plan"] --> SP2["Implement"]
        SP2 --> SP3["Gate & Test<br/><i>full guard loop</i>"]
        SP3 --> SP4["Audit<br/><i>2 passes</i>"]
        SP4 --> SP5["Regression & Final"]
        SP5 --> SP6["Ready Gate ⛔"]
        SP6 --> SP7["Ship"]
    end

    subgraph Full["🔒 Full (Standard + extras)"]
        FE1["User checkpoint<br/>before implementing"]
        FE2["Pass 3: Convergence<br/><i>re-review ALL changes</i>"]
        FE3["OWASP Top 10<br/>deep security dive"]
        FE4["Guardrails mandatory<br/>for ALL findings<br/><i>including cosmetic</i>"]
    end
```

### Full Mode Additions

| Addition | Description |
|---|---|
| **User checkpoint** | Phase 1 presents the plan and waits for explicit approval before implementing |
| **Pass 3: Convergence** | Re-reviews ALL changes from passes 1-2; loads `references/deep-audit.md` for OWASP Top 10 checklist |
| **Security Deep Dive** | Full OWASP Top 10 review, auth flow verification, data handling audit |
| **Mandatory guardrails** | ALL findings get guardrails, including cosmetic ones |
| **Expanded root cause scan** | Wider search radius for pattern occurrences |

---

## Toolchain Auto-Detection

Before running gates, the skill uses `scripts/detect-toolchain.sh` to auto-detect the project's stack:

```mermaid
flowchart TD
    DT["detect-toolchain.sh"] --> L{"Language?"}
    L -->|"package.json"| JS["JavaScript/TypeScript"]
    L -->|"requirements.txt / pyproject.toml"| PY["Python"]
    L -->|"go.mod"| GO["Go"]
    L -->|"Cargo.toml"| RS["Rust"]
    L -->|"Gemfile"| RB["Ruby"]
    L -->|"pom.xml / build.gradle"| JV["Java"]

    DT --> FW["Framework Detection<br/>React, Next, Vue, Svelte, Express,<br/>Django, Flask, FastAPI, Rails, Spring"]
    DT --> TL["Tool Detection"]
    TL --> LN["Linter: ESLint, Ruff, flake8, golangci-lint, Rubocop"]
    TL --> FM["Formatter: Prettier, Black, gofmt, rustfmt"]
    TL --> TC["Type Checker: tsc, mypy, pyright"]
    TL --> TR["Test Runner: Jest, Vitest, pytest, go test, cargo test"]
    DT --> DP["Deploy Target Detection"]
    DP -->|"supabase/config.toml"| SUP["Supabase"]
    DP -->|"vercel.json"| VER["Vercel"]
    DP -->|"netlify.toml"| NET["Netlify"]
    DP -->|"Dockerfile"| DOC["Docker"]
    DP -->|"serverless.yml"| AWS["AWS"]
    DP -->|".git + remote"| GIT["Generic Git"]

    DT --> OUT["JSON Output:<br/>{language, framework, linter,<br/>formatter, type_checker, test_runner,<br/>deploy_target, git_status, git_branch}"]
```

The gate runner (`scripts/run-gates.sh`) then uses this info to run the right tools with auto-fix.

### Supported Detection Matrix

| Category | Detected Tools |
|---|---|
| **Languages** | JavaScript, TypeScript, Python, Go, Rust, Ruby, Java |
| **Frameworks** | Next.js, React, Vue, Svelte, Express, Fastify, Django, Flask, FastAPI, Rails, Spring |
| **Linters** | ESLint, Ruff, flake8, golangci-lint, Rubocop |
| **Formatters** | Prettier, Black, gofmt, rustfmt |
| **Type Checkers** | tsc, mypy, pyright |
| **Test Runners** | Jest, Vitest, pytest, go test, cargo test, npm test |
| **Deploy Targets** | Supabase, Vercel, Netlify, AWS (Serverless/SAM), Docker, Generic Git |

---

## Dynamic Skill Delegation

sdlc-autopilot is an **orchestrator** — it controls the pipeline, but delegates domain expertise to other installed skills:

```mermaid
flowchart TD
    U["User: 'Fix the login page styling'"] --> SA["sdlc-autopilot activates<br/>(matches 'fix' + 'styling')"]
    SA --> P1["Phase 1: Scan installed skills"]
    P1 --> CHECK{"Any skill descriptions<br/>match this task domain?"}
    CHECK -->|"frontend-design skill matches<br/>'styling', 'UI changes'"| NOTE["Note in Implementation Brief:<br/>Delegate CSS/design to frontend-design"]
    CHECK -->|"react-doctor skill matches<br/>'React component'"| NOTE2["Note: Delegate React patterns<br/>to react-doctor"]
    CHECK -->|"No matches"| OWN["Use own best judgment"]

    NOTE --> P2["Phase 2: Implementation"]
    NOTE2 --> P2
    P2 --> DEL["When doing CSS work →<br/>Load frontend-design SKILL.md<br/>Follow its guidance"]
    P2 --> DEL2["When doing React work →<br/>Load react-doctor SKILL.md<br/>Follow its guidance"]

    SA -.->|"sdlc-autopilot controls"| PIPE["Pipeline phases,<br/>testing, auditing,<br/>guardrails, shipping"]
    DEL -.->|"Delegated skills control"| DOM["Domain-specific<br/>best practices"]
    DEL2 -.->|"Delegated skills control"| DOM
```

### Delegation Rules

- **Always** check the installed skills list — never assume what the user has
- If **none** are relevant → proceed with the agent's own best judgment
- If **multiple** are relevant → use each for its respective domain
- sdlc-autopilot remains in control of the **overall pipeline** (phases, testing, auditing)
- Delegated skills handle **domain-specific best practices** only
- **Fallback:** If the installed skills list is not available in context (some agents don't expose it) → skip delegation entirely and proceed with own judgment. Do not error or stall.

---

## Circuit Breaker & Safety Mechanisms

```mermaid
flowchart TD
    FIX["Fix an audit finding"] --> TEST["Run tests"]
    TEST -->|PASS| CONTINUE["Continue"]
    TEST -->|"NEW test failure<br/>(not from original change)"| CB["⚡ CIRCUIT BREAKER"]
    CB --> REV["REVERT the fix"]
    REV --> NOTE["Note in summary:<br/>'Identified but not fixed —<br/>requires manual review'"]
    NOTE --> NEXT["Move to next finding"]

    GC["Gate Cap: 3 auto-fix<br/>cycles max"] --> PROCEED["Proceed to audit<br/>even with remaining issues"]

    DEPLOY["Deploy fails"] --> ROLLBACK["Attempt platform rollback"]
    ROLLBACK -->|"Rollback succeeds"| REPORT["Report to user"]
    ROLLBACK -->|"Rollback also fails"| ERRORS["Capture both errors<br/>Present to user<br/>DO NOT retry"]
```

### Safety Hard Rules

| Rule | Description |
|---|---|
| **Never auto-deploy to production** | Preview/staging deploys are acceptable; production requires explicit user approval |
| **Warn before committing to main/master** | If on main/master, warn and offer to create a branch; user can say "commit to main" to override |
| **Never expose secrets** | Reference by variable name only (`$VAR_NAME`), never include values |
| **Circuit breaker on fix spirals** | If fixing a finding causes a NEW test failure → revert immediately |
| **Gate cap** | Maximum 3 auto-fix cycles, then proceed |
| **Hard stop at Ready Gate** | Phase 6 always waits for user confirmation |
| **No retry on deploy failure** | Attempt rollback once, then present errors to user |

---

## Token Budget Strategy

```mermaid
flowchart TD
    Q["Quick Mode<br/>~1,500 tokens"] -->|"Loads"| S1["SKILL.md only"]
    ST["Standard Mode<br/>~2,500 tokens"] -->|"Loads"| S1
    F["Full Mode<br/>~4,000 tokens"] -->|"Loads"| S1
    F -->|"Also loads"| DA["references/deep-audit.md<br/>(177 lines)"]

    SHIP["Phase 7: Ship<br/>+~600 tokens"] -->|"Loads once"| DEP["references/deployment.md<br/>(149 lines)"]

    RULE["Max 3 files loaded<br/>per invocation"]
```

Reference files are loaded **only when needed** — `deep-audit.md` only in Full mode Phase 4, `deployment.md` only in Phase 7. Token budgets are **skill instruction overhead only** — total pipeline cost depends on codebase size and files read.

---

## Graceful Degradation

The pipeline never fully breaks — it degrades gracefully:

| Missing | Behavior |
|---|---|
| **No shell commands** | Write tests + list commands for user. All phases still happen. |
| **No test framework** | Write tests in logical format. Suggest framework, don't block. Guardrail tests still written. |
| **No linter/formatter/typechecker** | Skip automated gates. Suggest setup, don't insist. |
| **No git** | Skip branching/commits/push. All other phases still happen. |
| **Context pressure (many/large files)** | If files exceed ~30% of context, summarize rather than load in full. Prioritize files from user's prompt. Don't load reference files unless full mode. |

---

## File Architecture

```
sdlc-autopilot/
├── SKILL.md                      ← Main pipeline (~305 lines, loaded on activation)
├── GUIDANCE.md                   ← This document
├── references/
│   ├── deep-audit.md             ← OWASP + guardrail patterns (Full mode only)
│   └── deployment.md             ← 6 platform deploy guides (Phase 7 only)
├── scripts/
│   ├── detect-toolchain.sh       ← Auto-detect language/framework/tools → JSON
│   └── run-gates.sh              ← Run linter/formatter/typechecker/tests
├── evals/
│   ├── evals.json                ← 10 test scenarios for validation
│   └── fixtures/01-10/           ← Realistic codebases with planted bugs
├── examples/                     ← Walkthroughs showing each mode
├── README.md / CONTRIBUTING.md / LICENSE.txt / CHANGELOG.md
```

The entire skill is **3 files at runtime** max: `SKILL.md` (always), `deep-audit.md` (full mode), `deployment.md` (deploy phase).

---

## Evals (Validation Test Suite)

The skill ships with 10 evaluation scenarios covering the full spectrum:

| # | Scenario | Mode | What It Tests |
|---|---|---|---|
| 01 | Cosmetic button styling | Quick | Low-risk change, minimal pipeline |
| 02 | Bug fix — search page crash | Standard | Root cause analysis, guard loop, regression tests |
| 03 | Feature — dark mode toggle | Standard | New feature, state management, test writing |
| 04 | Refactor — auth service extraction | Standard | Behavior-preserving refactor, contract tests |
| 05 | Security — SQL injection | Full | OWASP audit, parameterized queries, full guard loop |
| 06 | Audit finding — race condition | Standard | Concurrent data fetching, idempotency guard |
| 07 | No tooling project | Standard | Graceful degradation, manual test format |
| 08 | User override — force quick on high risk | Standard | Hard rule enforcement (rejects Quick for HIGH risk) |
| 09 | Circuit breaker trigger | Standard | Fix-break spiral detection, revert behavior |
| 10 | Null pattern — defensive coding | Standard | Null checks, type narrowing, guard pattern |

---

## Announcements

Each phase ends with a one-line, 15-word-max announcement:

```
"Bug fix identified. Implementing 3 steps."
"Implementation complete. Running checks."
"4 tests pass (2 new, 1 guardrail). Linting clean."
"Audit done. 2 issues: fixed 2, guarded 2, tested 2."
"All 6 tests pass. 2 guardrails verified."
"Ready gate passed. Summary above."
"Pushed to fix/search-keyboard. Commit: a1b2c3d."
```

---

## Critical Behaviors Summary

| Behavior | Rule |
|---|---|
| **Follow-ups** | Pipeline shipped → start NEW pipeline. During ready gate → "change X" returns to Phase 2. |
| **Mid-pipeline abort** | User says "stop"/"undo everything" → discard all changes (`git checkout -- .`), offer to delete created branch. |
| **Monorepos** | Auto-detect (`packages/`, `apps/`, `pnpm-workspace.yaml`, `lerna.json`). Scope tests and root cause scans to affected packages. |
| **Large codebases** | Cap ~10 files in Phase 1. Root cause scans use grep only — never scan entire codebase file-by-file. |
| **Project rules conflict** | SDLC provides the PROCESS. Project rules provide the STANDARDS. Style conflicts → project rules win. Process conflicts → SDLC wins. |
| **Can't find the bug** | Report what was searched. Ask ONE specific question. Never guess. |
| **Secrets** | Never in output or commits. Never add .env to git. Reference by variable name only. |
| **Stateless** | Each invocation is independent. No memory between pipeline runs. |
