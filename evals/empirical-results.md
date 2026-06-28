# Empirical Results

This document separates evidence from claims. It is safe to publish because it does not invent pass rates for agents that have not produced reproducible artifacts.

## Current Public Claim

As of 2026-06-28, this repository does not claim cross-agent pass rates. It provides:

- 26 outcome-focused eval scenarios in [evals.json](evals.json).
- Fixture-structure validation through [run-evals.sh](../scripts/run-evals.sh).
- Artifact-based agent-run checking through [run-agent-evals.py](../scripts/run-agent-evals.py).
- Optional metadata fields in [agent-run.schema.json](agent-run.schema.json) for agent name, version, surface, run time, and skill revision.

## Local Release Evidence

| Date | Evidence | Command | Result |
|---|---|---|---|
| 2026-06-28 | HTML spec validation and verifier regression | `node --test scripts/verify-pipeline.test.mjs docs/sdlc-autopilot-spec.test.mjs` | Passing: 2 tests |
| 2026-06-28 | Eval fixture and schema structure | `sh scripts/run-evals.sh` | Passing: 178 checks, 0 failures, 3 expected fixture warnings |
| 2026-06-28 | Full-mode Ready Gate verifier | `sh scripts/verify-pipeline.sh full` | Passing: 8/11 checks, 3 skipped for unavailable root runner, coverage artifact, and strict inversion |
| 2026-06-28 | Diff whitespace | `git diff --check` | Passing |

## Multi-Agent Evidence Bar

Do not publish an agent pass-rate claim unless every named agent has a run artifact directory containing:

- `meta.json` with `agent_name`, `agent_version` when available, `agent_surface`, `run_at`, `skill_version_ref`, `eval_id`, `mode`, and `summary`.
- `patch.diff` containing the actual patch applied to the fixture.
- `transcript.md` when transcript-based checks are used.
- A successful `python3 scripts/run-agent-evals.py --runs-dir <dir>` result.

Recommended first public campaign:

| Agent surface | Minimum eval subset | Why this subset |
|---|---|---|
| Terminal coding agent | 2, 5, 10, 16, 18, 23, 25, 26 | Covers Standard, Full, root-cause scanning, verification, confidence calibration, expert overlay, standards mapping, and trust model. |
| IDE agent mode | 2, 5, 10, 16, 18, 23, 25, 26 | Confirms the workflow survives an IDE execution surface. |
| Chat-only or limited-shell agent | 2, 7, 16, 18 | Confirms graceful degradation where commands may need to be run manually. |

## Agent Result Matrix

| Agent | Surface | Skill ref | Eval subset | Result | Artifact path |
|---|---|---|---|---|---|
| External agents | Not yet recorded | Not yet recorded | Not yet recorded | No public pass-rate claim | Not yet recorded |

## Reporting Rules

- Report pass rates only for artifacts that can be rerun.
- Keep manual assertion results separate from machine-check results.
- Name skipped evals and why they were skipped.
- Preserve transcripts for high-risk evals so confidence-calibration claims can be checked.
- Treat failures as useful release data, not as data to hide.
