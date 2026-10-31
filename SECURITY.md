# Security Policy

## Scope

This repository has three security-relevant areas:

1. The skill itself: `skills/sdlc-autopilot/`, `README.md`, `GUIDANCE.md`, and repository development scripts
2. Evaluation tooling and its locked dependencies under `scripts/`, `evals/runtime/`, and `evals/oracles/`
3. Intentionally vulnerable evaluation fixtures under `evals/fixtures/`

The fixtures exist to test whether agents can identify and repair bug classes like SQL injection, XSS, null crashes, and insecure auth patterns. They are not production code.

## Important Scanner Note

If you run repository-wide security scanning, expect findings inside `evals/fixtures/`.

Those findings are often intentional and do not describe the security posture of the skill implementation itself.

Recommended review approach:

- Review `skills/sdlc-autopilot/`, docs, and repository development scripts separately from `evals/fixtures/`
- Treat `evals/fixtures/` as non-production test assets
- Do not deploy or publish fixture code as an application
- If your security platform supports path scoping or exclusions for test fixtures, scope `evals/fixtures/` accordingly when assessing the skill package itself

## Dependency Review Note

The root repository does not ship a runtime application package. The central `evals/runtime/package.json` and lockfile describe tools actually executed during evaluation. Fixture manifests use that prepared runtime rather than independently unlocked external dependencies. Scan the central lockfile and harness dependencies; intentionally vulnerable fixture exclusions must not hide tooling vulnerabilities.

If you run dependency scanners such as Socket or Snyk, be explicit about whether you are scanning:

- the installable skill package under `skills/sdlc-autopilot/`, or
- the central evaluation runtime and harness, or
- the intentionally vulnerable sample fixtures used for evaluation

Those are different questions.

## Reporting a Real Vulnerability

If you find a vulnerability in the actual skill package, docs, or repository development scripts rather than the fixtures:

1. Open a private security report if your platform supports it.
2. Otherwise open an issue with enough detail to reproduce the problem safely.
3. Clearly state whether the issue affects the installable skill implementation or only an evaluation fixture.

## Execution boundary

Replay is for trusted patches. Temporary directories, sanitized environment variables
and completion records do not sandbox malicious code or attest installed dependency
integrity. Use independently controlled isolation without credentials/network for
adversarial agent campaigns. Review configured project commands before execution;
a `.sdlc-checks.json` file can run arbitrary code. Never place credentials in argv,
reports, patches, or review prompts.

## Maintained checks for this repository

The reviewed root `.sdlc-checks.json` invokes `gitleaks dir` with redaction and
inline allow comments disabled. CI provisions version 8.30.1 from official release
assets, verifies pinned SHA256 values, and runs clean/synthetic-secret/missing-tool
controls before scanning the current tree. No fixture path is excluded from this
secret scan. The helper never installs a scanner; absence is inconclusive. This
does not scan every historical commit or replace application threat review.

The validation runtime pins a narrow `@istanbuljs/load-nyc-config` → js-yaml 4.3.2
override to remove the sprintf-js advisory chain introduced by Jest. Its actual
YAML-loading API is exercised by `check-runner-adapters.py`. Recheck the lockfile
with npm audit when updating dependencies; never apply a forced major downgrade
merely because an advisory tool suggests it.

### Evaluation dependency review — 31 October 2026

The evaluation runtime additionally pins `glob` 14.0.2 and `minimatch` 11.0.1
through explicit overrides for
[GHSA-3g3m-2fjr-6pw4](https://github.com/advisories/GHSA-3g3m-2fjr-6pw4)
and [GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249).
These cross upstream dependency ranges, so native runner controls also exercise
Jest coverage and `test-exclude` include/exclude plus synchronous/asynchronous
file discovery. Retain those compatibility checks when revisiting the overrides.

The remaining [deepmerge advisory](https://github.com/advisories/GHSA-gcqx-w48m-w2h4)
is low severity and has no upstream patched version at this checkpoint. It remains
in Jest's evaluation-only configuration dependency chain; no exemption or audit
suppression is configured. Use trusted evaluation configuration and patches,
without credentials, and separate isolation for adversarial inputs. The existing
moderate-or-higher audit gate remains unchanged. Passing it is not a zero-advisory
or comprehensive security claim; reassess when an upstream fix becomes available.
