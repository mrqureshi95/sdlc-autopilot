# Follow-up deep audit and regression assessment

Date: 2026-10-21. Scope: the complete local skill package, references, helper and
evaluation code, fixtures, contributor/security guidance, examples, and CI. Work
continues on `codex/audit-remediation`; no installed-copy update, commit, push,
release, external-provider review, or deployment was performed.

## Assessment

The revised skill is an improvement on the audited original for the cases actually
checked. It preserves root-cause analysis, canonical contracts, targeted prevention,
practical test-first reproduction, bounded retries and proportional risk review.
It gives read-only audits a coherent path, removes unsafe copy-paste recipes and
implicit provider disclosure, and distinguishes missing evidence from success.

This is not a claim that all agents now work faster or produce better code. Local
runtime checks and independent instruction review support specific improvements;
a controlled cross-agent campaign and production integrations remain unmeasured.

## Fresh findings and fixes

| Finding | Consequence | Correction |
|---|---|---|
| Scans/provenance preceded project commands | A passing test could rewrite delivered source after it was scanned | Compare content, modes, HEAD, branch, index entries and flags after execution; drift makes final-state evidence inconclusive and lists changed paths |
| Evidence requirements were aggregated across projects | One package's tests/security command could cover a second package with no evidence | Validate every selected directory before executing anything; attach project scope and require evidence per project |
| TODO-tagged Node failures counted as real failures | A legitimate passing suite with known TODOs was rejected | Exclude skip/TODO events from both positive and failure counts; TODO-only remains inconclusive |
| Git assume-unchanged/skip-worktree flags hid edits | Modified source could be absent from scan/change evidence | Preserve flags, list masked paths, compare materialized contents/kind/mode with the index and include hidden edits; preserve legitimate absent sparse paths |
| Explicit empty configuration enabled Node fallback | A project requesting no configured checks still executed tests | Empty `checks` now disables fallback; behavioral evidence stays inconclusive |
| Contributor and scenario text described removed behavior | Future edits/evaluation could reintroduce generic rollback recipes or implicit model payloads | Align CONTRIBUTING, SECURITY and scenario setup with current architecture |
| Workflow evidence was broader than helper recognition | Valid native-runner/contract/rehearsal evidence could be mistaken for missing verification | Explicitly distinguish unsupported helper recognition from task adequacy; retain exact direct evidence without inventing counts or relabeling checks |

Each runtime finding was reproduced with a failing regression before its fix.
An independent local reviewer reproduced the runtime issues; a second reviewer
compared the instructions against the original and found the documentation drift.
No external provider was invoked. This audit's task-start snapshot captured the
already-dirty branch so earlier work was preserved rather than treated as new work.

## Controlled original-versus-revised comparison

`python3 scripts/compare-verifiers.py` creates disposable target repositories and
runs the original verifier from `6c1e8d1d8ea004a7398377005c71c09c516d14e7`
against the revised helper. These are eight chosen regression/control cases, not
a population pass rate or a benchmark of agent behavior.

| Case | Original | Revised | Interpretation |
|---|---|---|---|
| Cosmetic documentation edit | Exit 0 | Exit 0 | Valid simple work remains accepted |
| Named regression test | Exit 0 | Exit 0 | Supported useful execution remains accepted |
| Existing tests, no test churn | Exit 1 | Exit 0 | No arbitrary changed-test requirement |
| Clean read-only audit | Exit 1 | Exit 0 | Review does not demand implementation |
| Full outside Git | Exit 0 | Exit 2 | Missing provenance no longer means passed |
| Committed unsafe source under README edit | Exit 0 | Exit 1 | Worktree edits cannot hide branch source |
| Production filename with no named tests | Exit 0 | Exit 2 | Zero actual tests stays unverified |
| Failing test path containing spaces | Exit 0 | Exit 1 | Real failures are executed and detected |

All eight observed results matched these expectations during this audit.
The comparison explicitly preserves positive controls instead of measuring only
rejection. Other deliberate tradeoffs: helpers now require Python 3.10+, use
explicit project configuration, support fewer automatically recognized runners,
and do not claim generic inversion or stale coverage interpretation.

## Remaining limits

- Node, pytest and unittest have positive-count adapters. Other native suites,
  type/contract checks, migration rehearsals and benchmarks can provide valid
  direct evidence, but may not satisfy the helper's conservative test template.
- Security command labels and contextual review decisions are reviewed claims.
  No maintained security scanner is configured for this package; Full automated
  security evidence remains inconclusive.
- Pattern scans cover current changed readable text, not all history, ignored
  files, binary assets, symlink targets or an entire system. Full read-only review
  on a clean repo does not mean a repository-wide scanner ran.
- Pre/post observations cannot detect transient restored changes or attest
  dependency integrity. Commands and replay are not a malicious-code sandbox.
- Hashing source trees and explicit configuration carry setup/I/O cost; large-repo
  scalability, every platform/runner, mobile device behavior and remote CI were
  not benchmarked or validated by this local audit.
- Human judgment remains necessary for test relevance, architecture, scope and
  consequential residual risk. The installed copy still needs whole-package
  adoption through the supported workflow when desired.

Use this revision for reviewed local development with explicit project commands.
Use independently observed CI and appropriate human review for consequential work.
See the [one-page field guide](sdlc-autopilot-spec.html),
[original remediation ledger](remediation.md) and
[evidence record](../evals/empirical-results.md) for context and reproducible commands.

## Final local validation

- 47 Python runtime/harness regressions passed, with no skips (nine new regressions
  cover the additional runtime findings and valid-success cases).
- Three named Node package/docs/installed-entrypoint checks passed.
- Eight original-versus-revised controlled comparisons matched their expectations
  using both the local Node runtime and the supported bundled Node 24 runtime.
- Structural validation: 26 scenarios, 10 with semantic oracles, no errors.
- Locked fixture rerun: 35 baseline tests passed in 12 projects; the thirteenth
  exposed its intentional broken source import, reported separately.
- Five semantic before/after controls failed on the planted behavior and passed
  after hand-written fixes. These controls are not live-agent outcomes.
- Shell/Python syntax, Skill Creator validation and diff whitespace checks passed.
- The HTML guide was visually checked on desktop, at 375px mobile width without
  horizontal overflow, and in a one-page browser print export.
- Independent confirmation resolved every original runtime reproduction, including
  preservation of user index flags and valid expected-TODO behavior.

CI now includes the controlled comparison with full Git history available, but no
remote CI run was performed. Local configured checks are useful evidence; missing
security tooling is still disclosed rather than called a passed security review.
