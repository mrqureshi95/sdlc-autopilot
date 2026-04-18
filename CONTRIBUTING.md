# Contributing to SDLC Autopilot

## How to Add a Deployment Target

1. Edit `references/deployment.md`
2. Add a new section following this template:

```markdown
## Platform Name

**Detect:** What files/configs indicate this platform

**Deploy:**
\`\`\`bash
# Commands to deploy
\`\`\`

**Rollback:**
\`\`\`bash
# Commands to rollback
\`\`\`

**Health check:**
\`\`\`bash
# Commands to verify deployment
\`\`\`

**Common failures:**
- Failure scenario → fix
```

3. Add detection logic to the Detection Logic section (order matters — first match wins)
4. Add detection to `scripts/detect-toolchain.sh`

## How to Add Audit Patterns

1. Edit `references/deep-audit.md`
2. Add grep patterns to the relevant OWASP category, or create a new section
3. For each pattern, include:
   - The grep pattern to find the vulnerability
   - What to verify when found
   - The guardrail to add

## How to Add Guardrail Patterns

1. Edit `references/deep-audit.md`, Section 2 (Guardrail Pattern Library)
2. Follow this template:

```markdown
### Pattern Name
\`\`\`language
// GUARD: Description of what this prevents
function guardName(...) { ... }

// TEST: Verify the guardrail catches the dangerous pattern
test('description', () => { ... });
\`\`\`
```

Every guardrail pattern MUST include a paired test.

## How to Add Evaluation Scenarios

1. Edit `evals/evals.json` — add a new entry with:
   - `id`: next sequential number
   - `name`: kebab-case descriptive name
   - `prompt`: the user prompt to evaluate
   - `fixture`: path to fixture directory (optional)
   - `expected_mode`: quick | standard | full
   - `assertions`: list of human-verifiable criteria (checked manually, not automated)

2. Create a fixture in `evals/fixtures/<id>-<name>/`:
   - 5-10 files max
   - Include the bug/issue the test is evaluating
   - Include enough context for realistic behavior
   - For tests that verify audit findings, include hidden issues in adjacent code

## Development Principles

- **SKILL.md stays under 340 lines.** If you need to add content, find something to cut.
- **Reference files are loaded conditionally.** Don't add content to SKILL.md that's only needed in one mode.
- **Every guardrail has a test.** No exceptions.
- **Token efficiency matters.** Every line earns its keep.
- **Proportionality is key.** Don't gold-plate cosmetic findings. Don't skip security guards.

## Testing Changes

### Structural validation (automated)

Run `sh scripts/run-evals.sh` — validates fixture directories exist, JSON is well-formed, and source files are present. This checks the eval suite itself, not the skill.

### Skill evaluation (manual)

Assertions in `evals.json` are human-verifiable criteria, not automated tests. To evaluate the skill:

1. For each scenario in `evals.json`, create a new conversation with the agent
2. Set the working directory to the corresponding fixture
3. Provide the scenario prompt
4. Manually verify each assertion

Focus on:
- Mode selection correctness
- Fix-guard-test-verify loop execution for audit findings
- Guardrail proportionality
- Root cause pattern scanning
- Circuit breaker activation
- Logging proportionality (trivial vs non-trivial)

### Machine-checkable agent evals (artifact-based)

The repo also supports an artifact-based harness:

1. Create a run artifact directory per eval, for example `eval-runs/2-simple-bug-fix/`
2. Include:
   - `meta.json` matching `evals/agent-run.schema.json`
   - `patch.diff` containing the agent's patch for the fixture
   - `transcript.md` if you want transcript-based machine checks
3. Run `python3 scripts/run-agent-evals.py --runs-dir eval-runs`

The harness copies the fixture to a temp workspace, initializes git, applies the patch, runs `verify-pipeline.sh`, and evaluates any `machine_checks` declared in `evals/evals.json`.
