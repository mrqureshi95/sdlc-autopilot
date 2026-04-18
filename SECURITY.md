# Security Policy

## Scope

This repository contains two different kinds of content:

1. The skill itself: `SKILL.md`, `references/`, `scripts/`, `README.md`, `GUIDANCE.md`
2. Intentionally vulnerable evaluation fixtures under `evals/fixtures/`

The fixtures exist to test whether agents can identify and repair bug classes like SQL injection, XSS, null crashes, and insecure auth patterns. They are not production code.

## Important Scanner Note

If you run repository-wide security scanning, expect findings inside `evals/fixtures/`.

Those findings are often intentional and do not describe the security posture of the skill implementation itself.

Recommended review approach:

- Review the root skill/docs/scripts separately from `evals/fixtures/`
- Treat `evals/fixtures/` as non-production test assets
- Do not deploy or publish fixture code as an application
- If your security platform supports path scoping or exclusions for test fixtures, scope `evals/fixtures/` accordingly when assessing the skill package itself

## Dependency Review Note

The root repository does not ship a runtime application package. Many `package.json` files exist only inside fixtures so example projects can be exercised during evaluation.

If you run dependency scanners such as Socket or Snyk, be explicit about whether you are scanning:

- the root skill package contents, or
- the intentionally vulnerable sample fixtures used for evaluation

Those are different questions.

## Reporting a Real Vulnerability

If you find a vulnerability in the actual skill/docs/scripts rather than the fixtures:

1. Open a private security report if your platform supports it.
2. Otherwise open an issue with enough detail to reproduce the problem safely.
3. Clearly state whether the issue affects the root skill implementation or only an evaluation fixture.