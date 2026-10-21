# Evidence helper contract

Python 3.10+ and Git are required. Shell entrypoints locate their sibling
`evidence.py` and `node-test-reporter.mjs` from the installed skill directory.
Use absolute entrypoint paths from the target checkout, including subdirectories
and linked worktrees. Helpers do not install packages or contact providers.

## States and limits

| State | Meaning |
|---|---|
| pass | The named scoped observation satisfied its stated criterion |
| fail | A command/policy check failed; investigate cause (not necessarily a product defect) |
| inconclusive | Required evidence could not be collected or interpreted |
| not-applicable | The check does not apply to this task or is intentionally unsupported |

Exit 1 takes precedence over exit 2. Exit 2 reports missing required evidence.
Exit 0 means applicable required checks were satisfied; optional inconclusive
checks remain visible. Review on a clean repo needs no implementation diff.
Outside Git, diff provenance is inconclusive even in Full mode; no all-skipped
success message is possible. Fresh output counts are not tamper-proof evidence.

Quick/cosmetic work requires Git provenance and candidate review, but not invented
behavior tests. Standard behavior requires a positive supported test count.
Full behavior also requires a configured security command in each selected project.
Selected project directories must exist; one package cannot supply another’s evidence. “security” is a user
classification: inspect that it actually invokes an appropriate maintained tool
and scope; a label does not prove security coverage. Human threat/contract review
remains separate. Missing tools can support a useful unverified handoff, never a
claim that required checks passed.

## Change provenance and ownership

An explicit `--base REF` resolves to an exact SHA. Otherwise the helper reports a
local merge-base with origin's symbolic default, main, or master. It never fetches.
Without one, HEAD-only evidence is inconclusive; provide a correct explicit base.
The net base-to-current diff always includes committed branch and worktree edits,
plus untracked non-ignored paths. Names/statuses use NUL-delimited Git output;
renames include old paths and deletions remain explicit. Removed files are not
execution evidence. Ignored files and historical intermediate commits are outside
this net-diff scan; use a maintained history scanner when needed.

A snapshot records HEAD, dirty paths, file hashes, executable bits, file kinds, and timestamp outside the repo, using owner-only file permissions.
Later results separate pre-existing, changed-since-snapshot, mixed-preexisting,
and unknown paths. This is not line-level attribution or proof of who edited a
file. Review mixed hunks manually. Reports include invocation, root/cwd, exact
base selection, worktree digest, commands/cwds, return codes, elapsed times, and
output digests. Baselines and reports are local observations, not signed attestations.

## Reviewed project commands

Inspect `.sdlc-checks.json` before running any helper that executes commands. It is
repository-controlled executable configuration, not a trust boundary. Use explicit
`--project packages/api --project packages/ui` scopes for polyglot/monorepo work.
Project paths resolve from the Git root; command cwd resolves within each project.
Canonical wrappers such as `./gradlew`, `./mvnw`, `bundle exec`, or package-manager
scripts belong in this file after inspection. Detection lists manifests for all
languages present, configured commands, available executables, and unverified
runnability separately. It does not promise universal toolchain inference.

```json
{
  "version": 1,
  "checks": [
    {"name": "types", "kind": "type", "argv": ["./node_modules/.bin/tsc", "--noEmit"]},
    {"name": "unit", "kind": "test", "runner": "node-test", "argv": ["node", "--test", "./app behavior.test.mjs"]},
    {"name": "python", "kind": "test", "runner": "pytest", "argv": ["python3", "-m", "pytest", "tests", "-q"]}
  ]
}
```

Kinds: lint, format, type, test, security. Supported positive test-count adapters:
Node's named test events, pytest's fresh passed summary, unittest's fresh count
(excluding skips and expected failures), `jest-json`, `vitest-json`, and `junit`. Opaque exit-zero test
commands are inconclusive; don't disguise them as lint. Named tests, counts, and
exit status still cannot establish assertion quality or completeness. A no-test
Node file wrapper, skipped/todo-only run, or zero collection is not positive evidence.

For Jest/Vitest, configure the installed local runner or inspected package-manager
wrapper; the adapter appends its own reporter, output file, and non-watch flags:

```json
{"version":1,"checks":[
  {"name":"jest","kind":"test","runner":"jest-json","argv":["./node_modules/.bin/jest","--runInBand"]},
  {"name":"vitest","kind":"test","runner":"vitest-json","argv":["./node_modules/.bin/vitest"]},
  {"name":"other-language","kind":"test","runner":"junit","argv":["./scripts/test-with-junit","--output={report}"]},
  {"name":"secrets","kind":"security","argv":["gitleaks","dir",".","--redact","--no-banner","--ignore-gitleaks-allow"]}
]}
```

Choose only checks that apply. JUnit is a report contract: the reviewed project
wrapper must accept exactly one `{report}` substitution and export actual named
`testcase` elements to that path. It does not install Gradle/Maven/.NET/Ruby/Rust
runners or pretend their flags are interchangeable. JSON adapters reject competing
reporter/output/watch flags. Reports are created at fresh private external paths;
existing files are never consumed. Missing/malformed reports and zero/skip-only
runs are inconclusive. Named failures fail; JSON setup errors without executed
failures stay inconclusive, and explicit JUnit suite failures/errors fail the check.
Nonzero exit with an otherwise passing report is inconclusive. Report parsers are
bounded, reject XML entity declarations, and retain only counts/digests. A runner
or wrapper can fabricate results; freshness is not independent attestation.

Provision security tooling separately. `gitleaks dir` is an example maintained
secret check, not complete application security coverage. Review tool config and
ignore files as well as argv; avoid broad exclusions or unreviewed baselines.
`--ignore-gitleaks-allow` prevents inline allow comments suppressing findings.
Other applications may also need dependency, static, permission, and migration
checks selected for their actual threat model. Missing tools stay unverified.

Without configuration, verification has a narrow Node fallback for tracked and
untracked `.test/.spec.(js|mjs|cjs)` files in the selected project. It does not infer
Jest globals or run production `latest_data.js`. Configure the actual runner for
other projects. Existing tests are allowed; test churn is not required.

`run-gates.sh` runs only explicit configuration. Checks should be non-mutating.
It cannot prevent an opaque configured script from writing files; inspect wrappers.
Each command has a wall timeout (default 120s, `--timeout SECONDS`) and process-group
cleanup on supported POSIX hosts, including macOS. Output is bounded in memory
and omitted from reports to avoid copying secrets/hostile instructions; inspect
failures locally when needed. Disk consumption by a hostile process is not sandboxed.

An explicit fix invocation requires `--fix --file path` (repeat for more files).
A check may supply `fix_argv` with exactly one `{files}` placeholder. Files resolve
inside that project. Only those adapters run; inspect that they honor file scope.
No implicit `--fix`, formatting writes, npx downloads, or repository cleanup occurs.
For Go, configure `gofmt -l` on explicit files and treat nonempty output as failure
through a project wrapper; `gofmt -w .` is not recursive checking.

## Security, coverage, and inversion

The bundled scan checks whole current changed text files, not just added lines,
for a small disclosed set of credential/dynamic-evaluation/HTML-sink candidates.
It reports locations and fingerprints without matched contents. It does not
understand exploitability, comments, or legal suppressions. Review each match in
context; never exempt whole files/lines because they contain “test” or “config.”
Unreadable/oversized/binary/symlink paths are listed, not silently treated as scanned.
Use a configured maintained secret/security scanner for supported deeper coverage.
Do not print actual secrets; revoke/rotate exposed credentials and address history
under the owner's incident policy. Contextual review decisions are separate evidence.

Existing coverage artifacts are not consumed: freshness, source identity, scope,
and mapping cannot be inferred from basenames. Configure a fresh coverage command
and inspect exact source paths if coverage matters. No arbitrary percentage is
required by this skill. Automatic inversion is unsupported and exits 2; safe manual
before/after evidence needs isolated revisions, identical locked dependencies and
environment, named behavioral assertion failures, and positive after-fix execution.
Missing files, setup errors, or ENOENT are not regression inversion.

## Contextual decisions

To acknowledge an exact candidate, supply `--review-decisions /outside/reviews.json`:

```json
[{"fingerprint":"SHA256_FROM_REPORT","disposition":"false-positive","reason":"Explain the actual context and why the rule does not indicate a vulnerability."}]
```

`test-fixture` is for deliberately inert/vulnerable evaluation material whose use
and isolation were reviewed. `accepted-risk` remains inconclusive, rather than
turning risk acceptance into a security pass. Unreviewed matches fail the candidate
policy. Stale/unmatched fingerprints are rejected; the decision file digest is
recorded. Fingerprints bind the current worktree state as well as file/line/rule;
any tracked or non-ignored file edit requires refreshed decisions. External/ignored
configuration and runtime state still require contextual review. These decisions are claims requiring contextual review, not automatic
line suppressions or independent security evidence. Keep actual credentials out
of command arguments and reports; use an appropriate secret store/environment.
The helper records argv for provenance and cannot make sensitive argv safe.
Never place secrets directly in argv or inline command source; inspect configuration
before running it. Output digests refer to captured output, which may be truncated
when the output-limit state is reported.


## Helper support versus task adequacy

The workflow accepts task-appropriate characterization, type/contract checks,
migration rehearsals and benchmarks. This helper currently recognizes positive
test counts from Node, pytest, unittest, Jest/Vitest JSON, and fresh JUnit reports.
Reviewed Go/Rust/JVM wrappers can export the documented JUnit contract. A native
suite without supported reports or a contract-only check may still leave the
test requirement inconclusive even
when the agent has useful direct evidence. That means **unsupported recognition**,
not that verification was never performed. Report the exact native command,
observed results and scope separately; never relabel it as lint, fabricate a count,
or downgrade risk just to obtain a green helper. The helper's conservative Full
security template is likewise not a reason to install an irrelevant scanner or
ignore appropriate migration/contract evidence. Release adequacy is a contextual
risk decision, not the helper's exit code.

Explicit empty `checks` configuration disables fallback execution. When commands
run, reports attach their project scope and compare content, modes, HEAD, branch,
index entries and index flags before/after. Any observed drift makes final-state
evidence inconclusive; the earlier checks describe the input snapshot. Inspect the
listed paths and Git changes before rerunning. Do not loop blindly or add broad
ignore rules to hide source drift. Normal generated artifacts should follow the
project's reviewed ignore rules. Transient changes restored before observation,
ignored files, dependency integrity and concurrent hostile processes remain outside
this local observation contract.

Assume-unchanged/skip-worktree flags are preserved and listed. Existing masked
files are compared with the index without filters, including mode/kind, so hidden
edits join change evidence. Missing sparse-checkout paths remain outside the
materialized-file scan. Raw-versus-filtered comparisons can conservatively report
extra paths. Unverifiable masked paths are inconclusive; flags never silently grant
scan coverage.
