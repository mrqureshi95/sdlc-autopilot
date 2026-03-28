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

## How to Add Eval Test Cases

1. Edit `evals/evals.json` — add a new entry with:
   - `id`: next sequential number
   - `name`: kebab-case descriptive name
   - `prompt`: the user prompt to test
   - `fixture`: path to fixture directory (optional)
   - `expected_mode`: quick | standard | full
   - `assertions`: list of behaviors to verify

2. Create a fixture in `evals/fixtures/<id>-<name>/`:
   - 5-10 files max
   - Include the bug/issue the test is evaluating
   - Include enough context for realistic behavior
   - For tests that verify audit findings, include hidden issues in adjacent code

## Development Principles

- **SKILL.md stays under 300 lines.** If you need to add content, find something to cut.
- **Reference files are loaded conditionally.** Don't add content to SKILL.md that's only needed in one mode.
- **Every guardrail has a test.** No exceptions.
- **Token efficiency matters.** Every line earns its keep.
- **Proportionality is key.** Don't gold-plate cosmetic findings. Don't skip security guards.

## Testing Changes

After making changes, run the eval test cases:

1. For each test case in `evals.json`, create a new conversation with the agent
2. Set the working directory to the corresponding fixture
3. Provide the test prompt
4. Verify all assertions pass

Focus on:
- Mode selection correctness
- Fix-guard-test-verify loop execution for audit findings
- Guardrail proportionality
- Root cause pattern scanning
- Circuit breaker activation
- Phase announcement conciseness
