# Evaluation evidence and limits

No cross-agent controlled campaign or speed/quality comparison has been completed.
There is no claimed Codex/Claude/IDE pass rate, security coverage percentage, or
before/after outcome improvement statistic.

## Evidence layers

| Layer | What it can establish | What it cannot establish |
|---|---|---|
| `sh scripts/run-evals.sh` | Scenario/schema/fixture/lock references are structurally consistent | Agent adherence or product correctness |
| Python/Node package regressions | Confirmed helper/harness bypasses fail; supported success cases work | General agent behavior or absence of vulnerabilities |
| `scripts/check-fixtures.py` | Existing fixture tests execute with the locked central runtime | That planted defects are fixed |
| `scripts/check-oracles.py` | Hand-written before/after controls fail/pass evaluator-owned behavioral assertions | Any agent's success rate |
| `scripts/run-agent-evals.py` | Replay a supplied patch with harness-generated provenance and semantic checks where implemented | Authenticity of the agent identity/transcript, TDD timing, or all prose criteria |
| Human review / isolated live campaign | Contextual criteria when actually observed | A universal guarantee from one run |

Prose assertions always remain pending in machine replay output. Text-presence
checks are explicitly separate; an absent transcript cannot pass a negative check.
Metadata is schema-validated but is still a claim. The harness supplies its own
fixture/patch/skill/schema/oracle/runtime hashes, base revision, commands/cwds,
timestamps, environment versions, and cleanup evidence. These are unsigned local
observations, not independently trusted attestations.

## Reproduce

Use Python 3.10+ and a supported Node LTS version. The checked-in runtime is pinned
and locked; Node 24.15+ in the 24 LTS line is supported by this dependency set.

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -q
node --test scripts/verify-pipeline.test.mjs scripts/skill-package.test.mjs docs/sdlc-autopilot-spec.test.mjs
sh scripts/run-evals.sh
python3 scripts/prepare-eval-runtime.py --output /tmp/sdlc-runtime-UNIQUE
python3 scripts/check-fixtures.py --runtime-dir /tmp/sdlc-runtime-UNIQUE
python3 scripts/check-oracles.py --runtime-dir /tmp/sdlc-runtime-UNIQUE
```

Runtime preparation alone acquires public packages and runs no lifecycle scripts.
Replay does not install dependencies. For a supplied run create a directory named
`15-python-bug-fix` (or `15`) with `patch.diff`, `meta.json` matching
[the closed schema](agent-run.schema.json), and `transcript.md` for text checks.

```sh
python3 scripts/run-agent-evals.py --runs-dir /path/to/runs --eval-id 15 --execute
```

Without `--execute`, this checks artifacts only and returns inconclusive behavioral
evidence. With it, supplied code executes in a disposable directory. That is not a
security sandbox: use trusted patches or an independent no-network/no-credentials
sandbox. Evaluator-owned oracles use fresh completion records, never stdout success
markers; early exit is inconclusive. They are outside the patch workspace but
share the evaluated process/host and can still be forged by malicious code. A
nonce prevents stale reuse, not deliberate in-process tampering. Do not expose credentials or live
infrastructure to a campaign.

## Local remediation evidence (2026-10-21)

The remediation ledger records scope and intentional replacements. Local evidence
includes adversarial regressions, locked fixture baselines, hand-written oracle
controls, and one independent same-host forward test. The forward test preserved
pre-existing edits and observed a named regression fail before/pass after; clean
Full review executed no project commands. Its discovered runtime/reporting defects
were fixed with regression coverage.

Final counts and observations are added after the last verification run; count
changes are not quality claims. CI is configured for Linux/macOS but has not been
run remotely during this local task. No real deploy, migration, rollback, prune,
provider code review, push, or release was executed.

## Still unmeasured

- A controlled live-agent campaign across models, hosts and adversarial tasks.
- Mobile keyboard/layout behavior on devices; jsdom checks only component behavior.
- Broad runner/toolchain/migration/deployment integrations and scanner efficacy.
- Resistance to malicious code controlling the same host or forged execution logs.

Use reviewed explicit commands and independently observed CI/human review where
consequential risk warrants it. Installation-format support is not behavioral proof.

## Final observed local checks

On 2026-10-21, macOS:

- 38 Python runtime/harness regressions passed, with no skips.
- 3 named Node package/docs/installed-entrypoint checks passed.
- Structural validation found 26 scenarios, 10 with semantic oracles, and no errors.
- 35 baseline tests passed across 12 fixture projects; the thirteenth exposed its
  intentional broken source import and was reported separately, not as passing tests.
- Five hand-written semantic controls (pagination, health, strict input validation,
  and two SQL fixtures) produced assertion failure before and success after the fix.
- Shell/Python syntax, Skill Creator validation, and diff whitespace checks passed.
- The independent re-audit's original failures no longer reproduced; its bounded
  confirmation found no material mismatch. This is one local review, not a campaign.
- Configured package gates passed. Full evidence remains inconclusive without a
  configured maintained security scanner; contextual fixture/regex matches are
  reviewed decisions, not an independent security clearance.

These are observations of this local revision. Remote CI and broader toolchains
remain unobserved. No all-agentic-behavior validation is claimed.

## Follow-up full re-audit (2026-10-21)

The subsequent user-requested audit added nine meaningful runtime regressions;
47 Python checks and three Node checks now pass without skips. It also compared
eight disposable controlled cases against the original audited verifier. Valid
simple edits and named tests remain accepted, four former false-green cases are
rejected, and legitimate existing-test/read-only-review cases are accepted.
These are selected helper comparisons, not a live-agent pass rate. The locked
fixture/oracle reruns retained their earlier observed outcomes. Additional findings,
fixes, usability tradeoffs and independent confirmation are recorded in the
[follow-up audit](../docs/re-audit.md).

## Provider-neutral package-readiness follow-up (2026-10-21)

The earlier missing-security-tool observation is superseded by the configured
Gitleaks scan and controls in the [release-readiness audit](../docs/release-readiness.md).
The follow-up adds fresh Jest/Vitest/JUnit adapters and actual three-host CLI
installation smoke checks. It does not establish cross-model behavior or turn
prior manual replay controls into live-agent results. See that audit for final
local check counts, security scope, dependency remediation and remaining limits.

## Version 2.0.0 publication and future effectiveness evidence

The dated sections above describe successive local audit checkpoints. Final
release scope and current remote-check links are in the
[2.0.0 release notes](../docs/releases/v2.0.0.md). The
[measurement protocol](../docs/measuring-value.md) separates real-project
observations from controlled paired comparisons. The field-study directory
contains an optional template, not usage records or measured improvement.
