# Contributing to SDLC Autopilot

The canonical workflow is `skills/sdlc-autopilot/SKILL.md`. Keep it concise and put
conditional detail in the relevant reference. Preserve user intent, existing
project conventions, instruction hierarchy, and actual authorization boundaries.
Do not add ceremonial phases or promise guarantees the package cannot enforce.

## Runtime changes

Reproduce evidence/safety defects in disposable repositories before changing the
helper. Cover meaningful outcomes: wrong success/failure, missing scope, path
handling, stale provenance, zero execution, or unintended mutations. Preserve
legitimate supported success cases as well as rejecting bypasses. Changes to
assertion relevance, risk judgment, or agent behavior need contextual evaluation;
keyword/heading checks do not prove them.

Checks are reviewed explicit argv arrays in `.sdlc-checks.json`, with project scopes
and bounded execution. They must not implicitly fetch unpinned tools or rewrite a
repository. New adapters should use maintained runner evidence, reject zero or
uninterpretable execution, distinguish setup failures where supported, and document
versions and limits. An exit-zero opaque script is not proof that tests ran.
Keep unsupported evidence inconclusive without declaring useful work impossible.

## Security and deployment guidance

Use current primary framework/vendor sources. Explain the trust boundary, context,
evidence, and residual risk. Prefer maintained platform controls to handwritten
pseudo-sanitizers or grep-based vulnerability claims. A pattern match is a review
candidate, not a confirmed exploit. Contextual decisions must not silently exempt
whole test/config files.

Deployment additions belong in the platform decision workflow: exact identity,
environment/revision, reviewed preview/plan, health checks, data compatibility and
specifically authorized recovery. Do not add universal deploy/rollback recipes,
first-match platform inference, pruning, stack deletion, or user-work stashing.
Test with mocks or isolated disposable fixtures, never live infrastructure.

## Evaluation changes

Add realistic prompts and human criteria to `evals/evals.json`, aligned with the
actual fixture and the current skill. Evaluate outcomes rather than a mandatory
implementation or phrase. Avoid requiring unrelated fixes or implicit external
review. Add evaluator-owned semantic oracles where practical and exercise their
before/after and setup-failure behavior.

External dependencies belong in the exact-pinned `evals/runtime/package.json` and
checked-in lockfile, not independently unlocked fixture manifests. Runtime setup
is separate from replay and disables lifecycle scripts. See README for supported
Node versions and preparation commands.

Keep these evidence types separate:

- Structure: `sh scripts/run-evals.sh` validates scenario/package references.
- Execution: Python/Node regressions, fixture baselines and oracle controls.
- Replay: `run-agent-evals.py` validates supplied artifacts by default;
  `--execute` runs trusted supplied code in disposable directories, not an OS sandbox.
- Human judgment: prose criteria remain pending until actually reviewed.

Run metadata must match the closed schema. The harness generates provenance;
self-reported flags, identity, transcripts and summary wording are not execution
proof. Never infer a live-agent pass rate or speed gain from structure checks,
hand-written control patches, or one local review.

## Local verification

Use the commands in README for runtime/package tests and locked fixture/oracle
checks. `python3 scripts/compare-verifiers.py` reproduces selected behaviors against
the original audited commit; this is a controlled helper comparison, not an agent
benchmark. Update the evidence contract and examples when behavior changes. Report
checks actually run, failures, unsupported areas and consequential residual risk.
No push, release, installed-copy update or deployment is implied by contributing.

Public package changes also need the locked native-runner, standalone installer
and maintained-scanner controls listed in README. Keep the bundled MIT notice
identical to the canonical root license. Record model-host compatibility separately
from actual agent effectiveness; update release-readiness evidence without rewriting
historical observations as if earlier audits already had the new capabilities.
