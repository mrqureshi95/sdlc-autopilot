# Optional parallel delivery

Use only for requested/authorized delegation with separable work. Keep the core
SDLC risk, evidence, confidentiality, and publication rules. Parallelism is an
execution choice, not permission to change scope, skip acceptance, or contact
another provider. Inherit the host's model/effort settings unless the user selects
otherwise; no model ranking is required.

## Plan the boundary before dispatch

Keep one canonical acceptance gate and one integrator. Start with one or two
bounded workers. The integrator records the actual specification/design sources,
acceptance criteria, dependency order, shared interfaces, and relevant edge cases
in the project's existing task/issue system. A worker cannot infer new product
requirements from its own implementation. Split independent work inside a gate;
do not mark dependent gates accepted early. Sequence coupled schema, identity,
crypto, or shared-contract changes under one owner.

Copy [task-plan.example.json](../assets/parallel-delivery/task-plan.example.json)
and replace its illustrative values. The templates are **not dispatchable** until
populated with real bindings and `check-plan --live` passes. Version 1 records:

- `base`: full committed Git SHA; `gate`: canonical acceptance gate identifier.
- `shared_paths`: repository-relative paths reserved for the integrator.
- `tasks`: one or two tasks with unique `id`, disjoint `owned_paths`, an absolute
  `worktree`, `branch`, distinct `ports`, unique `database` namespace, absolute
  `output_dir` inside that worktree, and `required_checks` objects with fixed
  `name` and `kind` (for example `{"name":"behavior","kind":"test"}`).

Use repository-relative file/directory prefixes for ownership. Directory prefixes
include descendants. The assignment must also name expected outcomes, inspected
check commands and their scope; check names alone are not commands. Neither the
plan nor its checker launches agents, provisions databases, or executes tests.
Handoff check names and kinds must match the plan; do not relabel a required test
as lint or another kind to evade its positive execution count.

Create each worktree from the recorded base after preserving user work. Separate
database/schema names, local services, ports, generated reports, and temporary
outputs; worktrees alone do not isolate these. Validate live worktree/base/branch
bindings before dispatch. Keep credentials and production/deployment authority
outside worker access using actual host permissions; worktrees are not security
sandboxes. A shared local runtime needs an explicit owner and safe allocation.
Use canonical absolute paths from `pwd -P`/path resolution consistently, including
platform aliases such as `/tmp` versus `/private/tmp`.

Before dispatch, the integrator provisions `.delivery-local/` separately inside
each worker for its `output_dir`. Exclude only this local output directory so
reports do not make an otherwise committed candidate dirty. Run setup serially;
linked worktrees may share Git's `info/exclude`. Append the exact pattern if absent,
preserving all existing entries; do not replace that file or edit shared tracked
`.gitignore` policy:

```sh
WORKTREE=/absolute/canonical/worker-path
WORKER_EXCLUDE=$(git -C "$WORKTREE" rev-parse --path-format=absolute --git-path info/exclude)
python3 - "$WORKTREE" "$WORKER_EXCLUDE" <<'PY'
import pathlib, sys
worker, exclude = map(pathlib.Path, sys.argv[1:])
exclude.parent.mkdir(parents=True, exist_ok=True)
pattern = "/.delivery-local/"
existing = exclude.read_text() if exclude.exists() else ""
if pattern not in existing.splitlines():
    with exclude.open("a") as handle:
        handle.write("\n" + pattern + "\n")
(worker / ".delivery-local").mkdir(mode=0o700, exist_ok=True)
PY
git -C "$WORKTREE" check-ignore --quiet .delivery-local/
```

This intentional local exclusion is for generated output only; it is not a secret
store or an ownership bypass. Retain and inspect the referenced evidence through
integration; publish selected reviewed evidence through the project's artifact
process when authorized. Do not broaden exclusions to hide source drift.

```sh
python3 "$SDLC_SKILL_DIR/scripts/parallel_delivery.py" check-plan --plan PLAN.json --repo REPO
python3 "$SDLC_SKILL_DIR/scripts/parallel_delivery.py" check-plan --plan PLAN.json --repo REPO --live
```

## Worker, review, integration

1. **Build:** read the assignment and relevant contracts; change only owned paths.
   Stop the affected task for an ownership/interface conflict and report it to the
   integrator. Run focused behavioral/contract/security checks appropriate to the
   change once after final relevant edits. Commit the candidate without unrelated
   work. Do not edit the canonical tracker, shared contracts, check policies, or
   another worker's files unless the integrator explicitly reallocates ownership.
2. **Hand off:** populate [handoff.example.json](../assets/parallel-delivery/handoff.example.json)
   from observed results. Bind `task`, original `base`, full committed `candidate`,
   named checks, command exit codes, real positive test counts, and SHA-256 digests
   of retained evidence inside `output_dir` (absolute or output-directory-relative
   evidence paths). Report blockers and residual risks;
   never label interrupted, skipped, zero-test, or unsupported runs as passed.
   Each evidence file should retain the command, environment/scope, tested source
   identity, and native runner output needed to inspect the claim. Keep transient
   caches outside retained evidence and exclude secrets from both.
3. **Review:** a fresh reviewer inspects the actual candidate diff against the
   agreed base, requirements and raw results. It checks missing boundaries,
   ownership drift, altered tests/controls, and dependencies rather than trusting
   the builder's summary. Independent review reduces mistakes but cannot guarantee
   correctness or security. Fixes return to the builder; the reviewer does not approve
   its own implementation. Host permissions must enforce any read-only sandbox:
   reviewer instructions alone cannot. External-provider review needs authorized
   destination and payload scope; model availability grants no consent.
4. **Integrate:** the integrator applies reviewed changes one at a time, resolves
   conflicts, and verifies the resulting combined revision at meaningful merge
   milestones. Required repository CI checks and branch protection must prevent
   merging failed/missing checks; verify those settings and actual run results.
   Worker-local success and this helper's exit code do not substitute for CI or
   combined application verification. Keep protected policy/workflow ownership
   under independent review so a worker cannot self-authorize weaker checks.

```sh
python3 "$SDLC_SKILL_DIR/scripts/parallel_delivery.py" check-handoff --plan PLAN.json --report HANDOFF.json --repo REPO
```

The helper validates structure, declared Git/path ownership and retained evidence
bindings. It does **not** prove the commands ran, reports are truthful, tests are
adequate, agents were sandboxed, CI protection is active, or code is secure. The
integrator observes execution and inspects native reports; independent review and
required CI remain separate controls. Exact fields are illustrated in the assets;
all-zero SHA values mean **unset**, and the examples are not accepted run evidence.

## Avoid repeated work; recover honestly

Reuse existing evidence only when the tested source, dependencies, environment,
command/configuration and relevant consumers still match. Say what was reused and
why it applies. A source edit, changed dependency or integration conflict invalidates
affected evidence, not necessarily every unrelated check. Run focused worker checks;
reserve the appropriate combined regression for integration milestones. Never merge
separate partial runs into a claim that one complete command passed. Keep physical
device/provider/browser/restore and qualified human obligations explicitly pending;
host tests or emulator results do not establish them.

On interruption retain worktrees, commits, logs, owned resources and blockers. On
resume inspect actual Git state, task ownership, candidate and resource availability;
recheck applicable bindings and rerun only affected/missing checks. Never reuse an
interrupted report as success or kill another task's services. Clean up only owned
resources after integration and preservation. Track accepted delivery time, rework,
integration failures and escaped defects during a small pilot before adding workers.

The [builder](../assets/parallel-delivery/builder.toml) and
[reviewer](../assets/parallel-delivery/reviewer.toml) files are optional Codex agent
configuration templates. Adapt paths and register them through the host's supported
configuration. They add no orchestrator service or automatic dispatch. Provider-
neutral hosts can use the same task/handoff contract with their own permissions.
