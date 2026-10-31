# SDLC Autopilot

A skill for risk-proportional software changes and read-only code review. It helps
agents reproduce bugs, preserve canonical contracts and user work, add useful
prevention, and report verification honestly. It is guidance, not a security or
correctness guarantee.

## Install and use

Installers supporting the Agent Skills package format should copy the entire
`skills/sdlc-autopilot/` skill folder. Do not copy `SKILL.md` by itself. Existing
skills.sh users can select the nested package:

```sh
npx skills add mrqureshi95/sdlc-autopilot --skill sdlc-autopilot
```

Select a host explicitly when needed (project-local installation is the default):

```sh
npx skills add mrqureshi95/sdlc-autopilot --skill sdlc-autopilot -a codex
npx skills add mrqureshi95/sdlc-autopilot --skill sdlc-autopilot -a claude-code
npx skills add mrqureshi95/sdlc-autopilot --skill sdlc-autopilot -a opencode
```

This is an explicit installer action; verification never runs an installer.
The skill uses the open [Agent Skills format](https://agentskills.io/specification),
plain instructions, and local scripts. It requires no provider SDK, API key,
subscription, or mandatory external model review. Codex, Claude Code, and other
[compatible hosts](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)
can load it. DeepSeek and other models can use it through a capable host; a model
name alone does not supply skill discovery, files, a shell, or permissions.

With no native skills support, give the agent the complete local package and ask
it to read `SKILL.md`. With no execution tools, it can apply the reasoning workflow,
but must report runtime checks as unverified. Follow the host's instruction hierarchy
and permission model. Installation compatibility does not establish equal agent
behavior; no controlled live Codex/Claude/DeepSeek effectiveness comparison is claimed.
For host-specific setup see [Codex](https://developers.openai.com/codex/skills/)
and [Claude](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).

To try an uncommitted local revision, point the agent directly to
`skills/sdlc-autopilot/SKILL.md` in this checkout. Updating an installed copy requires
an explicit whole-package reinstall/copy through the host's supported workflow.
Repository source is canonical. Installed copies are independent and require a complete
package update; inspect `metadata.version` in the installed SKILL.md to confirm it.
For updates between tagged releases, compare the complete package with the chosen
Git commit as well; the version field alone does not identify those changes.
Version 2.0.0 changes helper verification/exit contracts; see the [changelog](CHANGELOG.md).

Example requests:

```text
Use SDLC Autopilot to fix this pagination bug and verify the first and last pages.
Use SDLC Autopilot for a read-only review of this patch; report findings only.
```

## Workflow

Choose task type (implementation, review, deployment) separately from risk.
Quick handles cosmetic/mechanical/disposable work. Standard handles ordinary
behavior. Full adds targeted review for consequential security, contract, data,
or delivery changes. File count and “careful” do not determine risk.

Fix-Guard-Test-Verify means: reproduce when practical, fix the cause, add the
lightest effective prevention, and verify the actual outcome. Test intent follows
the task: regression, characterization, contract, migration rehearsal, or benchmark.
Existing tests may suffice. Unrelated findings are triaged rather than silently
expanding scope. Authorized reversible work proceeds without redundant pauses.

Read-only review neither implements nor demands an implementation diff. External
model review is opt-in for a named destination and scoped redacted payload.
Deployment requires actual authority for the exact environment/action; no generic
rollback or cleanup recipes are executed.

### Optional parallel delivery

When delegation is explicitly authorized, the
[parallel-delivery guide](skills/sdlc-autopilot/references/parallel-delivery.md)
adds one integrator, one or two bounded workers, disjoint path ownership, isolated
resources, and review before integration. Bundled plan/handoff examples and a
read-only checker validate declared Git, ownership and retained-evidence bindings.
They do not dispatch agents, sandbox workers, run tests, or prove reports truthful.
The builder/reviewer TOML files are optional Codex templates; other hosts can use
the same provider-neutral task and handoff contract.

Before expensive validation, check prerequisites and resource ownership. After a
failure, retain the result, diagnose the first useful cause, and qualify the fix
with focused checks before repeating the full run. Reuse evidence only when its
source, dependencies, environment and relevant scope still match. On resumption,
check whether an owned process is still running before starting its replacement.

## Evidence helpers

Python 3.10+, Git, and a POSIX host are required for runtime helpers. Node 22+ is
needed only for the Node adapter. The package is:

```text
skills/sdlc-autopilot/
  SKILL.md
  LICENSE.txt
  references/evidence.md
  references/self-verification.md
  references/deep-audit.md
  references/deployment.md
  references/parallel-delivery.md
  assets/parallel-delivery/
    task-plan.example.json
    handoff.example.json
    builder.toml
    reviewer.toml
  scripts/evidence.py
  scripts/parallel_delivery.py
  scripts/node-test-reporter.mjs
  scripts/detect-toolchain.sh
  scripts/run-gates.sh
  scripts/verify-pipeline.sh
  scripts/verify-inversion.sh
```

Set `SDLC_SKILL_DIR` to the absolute installed skill folder, then run commands from
the target checkout. Capture a baseline before editing; store it outside the repo.

```sh
python3 "$SDLC_SKILL_DIR/scripts/evidence.py" snapshot --output /tmp/my-task-start-UNIQUE.json
sh "$SDLC_SKILL_DIR/scripts/detect-toolchain.sh" --project packages/api
sh "$SDLC_SKILL_DIR/scripts/verify-pipeline.sh" standard --base main --baseline /tmp/my-task-start-UNIQUE.json --project packages/api --json
```

Helpers report **pass**, **fail**, **inconclusive**, and **not-applicable**.
Exit 0 means applicable required checks were satisfied, 1 an observed check/policy
failure, and 2 missing required evidence. Neither exit 0 nor a pattern scan proves
readiness. Exact base/cwd/commands/digests and path-level attribution are reported.
Branch and worktree changes are combined; untracked paths and filenames with spaces
are handled without shell splitting.

Commands in `.sdlc-checks.json` must be inspected before execution. Gates are
non-mutating by convention and explicit configuration, with scoped opt-in fix
adapters, no implicit npx downloads, and portable timeouts. Helpers do not infer
all toolchains or automatically cover monorepos. Test adapters support Node, pytest,
unittest, Jest JSON, Vitest JSON, and fresh JUnit XML from reviewed wrappers.
Opaque/zero-test execution stays unverified. Helpers support POSIX systems; native
Windows process handling is not implemented. Windows users need a suitable POSIX
environment (for example WSL) for helpers, or use direct project checks.
Existing coverage files and assertion counts are not quality evidence. Automatic
inversion is unsupported. See [the complete evidence contract](skills/sdlc-autopilot/references/evidence.md).

## Verify this package locally

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -q
node --test scripts/verify-pipeline.test.mjs scripts/skill-package.test.mjs docs/sdlc-autopilot-spec.test.mjs
sh scripts/run-evals.sh
```

The evaluation runtime uses pinned dependencies and a checked-in npm lockfile.
Use Node 24.15+ in the 24 LTS line (or a version supported by every locked package).
Prepare it once in a new external directory; replay never installs dependencies.

```sh
python3 scripts/prepare-eval-runtime.py --output /tmp/sdlc-runtime-UNIQUE
python3 scripts/check-fixtures.py --runtime-dir /tmp/sdlc-runtime-UNIQUE
python3 scripts/check-oracles.py --runtime-dir /tmp/sdlc-runtime-UNIQUE
python3 scripts/check-runner-adapters.py --runtime-dir /tmp/sdlc-runtime-UNIQUE
python3 scripts/check-installation.py --runtime-dir /tmp/sdlc-runtime-UNIQUE
python3 scripts/run-agent-evals.py --runs-dir /path/to/runs --eval-id 15 --execute
```

The repository configures maintained secret scanning through Gitleaks. Provision
it explicitly; helper runs never download it. The preparer verifies the official
8.30.1 archive against a pinned SHA256 and writes only to a new directory:

```sh
python3 scripts/prepare-security-tool.py --output /tmp/sdlc-security-UNIQUE
python3 scripts/check-security-tool.py --binary /tmp/sdlc-security-UNIQUE/gitleaks
PATH="/tmp/sdlc-security-UNIQUE:$PATH" sh skills/sdlc-autopilot/scripts/run-gates.sh --json
```

If Python cannot validate the download certificate, repair its TLS trust store;
do not disable certificate verification. CI explicitly provisions the same scanner.
Missing scanners remain inconclusive. This scan covers current-tree secrets,
not dependency vulnerabilities, authorization correctness, or all of Git history.
Each consuming project configures appropriate checks; Full mode requires scoped
security evidence, and relevant threat/contract review still matters.

Replay executes supplied code in disposable directories, **not an OS sandbox**.
Use trusted patches or an external sandbox without network/credentials. Semantic
oracles live outside the supplied patch workspace, but local code can still tamper
with its host; stronger adversarial evaluation requires isolation and independent
observation. No real deployment is part of evaluation.

Structural checks, executable replay, text-presence checks, and human judgments
are separate. No cross-agent pass rates, security coverage percentages, or speed
gains are claimed. See [evaluation evidence and limits](evals/empirical-results.md)
and [the remediation ledger](docs/remediation.md).

The [one-page field guide](docs/sdlc-autopilot-spec.html) visualizes the workflow.
The [follow-up deep audit](docs/re-audit.md) records additional fixes, tradeoffs, and
eight controlled original-versus-revised helper comparisons. Reproduce those with
`python3 scripts/compare-verifiers.py`; these are not live-agent outcome statistics.

## Public release readiness

The latest tagged release is **v2.0.0**. The default `main` branch additionally
contains the parallel-delivery controls, validation-efficiency guidance and
evaluation dependency patch listed under [Unreleased](CHANGELOG.md#unreleased).
Installing from the repository's default branch includes those changes; the
v2.0.0 release archive remains the original tagged package.

The [security policy](SECURITY.md#evaluation-dependency-review--31-october-2026)
records current evaluation dependency fixes, compatibility checks and the remaining
unpatched low-severity advisory. These evaluation dependencies are separate from
the installable skill package.

Version **2.0.0** provides provider-neutral guidance and explicit local evidence
helpers. See [release notes](docs/releases/v2.0.0.md), the [prepublication audit](docs/release-readiness.md),
and [GitHub Actions](https://github.com/mrqureshi95/sdlc-autopilot/actions/workflows/validate.yml)
for scope, reproduced controls and current CI. Public installation retrieves the
published source; development edits require their own verification and publication. The [skills.sh FAQ](https://www.skills.sh/docs/faq)
describes automatic leaderboard inclusion through installation telemetry; listing
is not certification or proof of agent effectiveness. No public listing or remote
CI success is asserted by a local smoke test.

## Measuring usefulness

Use [the practical measurement protocol](docs/measuring-value.md) and
[optional local task record](evals/field-study/usage-record.template.json) to collect
acceptance, independently checked behavior, defects, human rework, time and friction.
Keep real-project observations separate from controlled paired comparisons with
and without the skill. Templates are not results. No usage data is collected or
uploaded by the skill, and no model-effectiveness percentage is claimed.

## Sources

- [Canonical skill](skills/sdlc-autopilot/SKILL.md)
- [Design guidance](GUIDANCE.md) · [Browser overview](docs/sdlc-autopilot-spec.html)
- [Security policy](SECURITY.md) · [Changelog](CHANGELOG.md) · [License](LICENSE.txt)
