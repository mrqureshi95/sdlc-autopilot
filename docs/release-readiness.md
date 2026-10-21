# Provider-neutral public-release audit

Prepublication audit date: 2026-10-21. Current release information is in
[the v2.0.0 release notes](releases/v2.0.0.md); publication/CI and installed-copy
state below describe the earlier audit checkpoint, not the later release. This audit follows the remediation and full re-audit; earlier
observations are historical. This is a finite package-readiness assessment, not a
claim of universal model effectiveness or production security certification.

## Practical value and supported use

SDLC Autopilot is useful for coding agents that tend to finish after producing a
plausible patch. It gives them a reusable way to choose scope and risk, reproduce
the relevant behavior, preserve contracts and user edits, prevent recurrence,
and distinguish observed results from missing evidence. Read-only reviews do not
require artificial code changes. Cosmetic tasks do not inherit heavyweight gates.
Repository checks and independently observed CI should enforce important requirements.

The instructions and stdlib helpers call no model/provider API and require no
provider key or subscription. A model such as DeepSeek can use the skill through
a host that supplies instruction loading, repository access and execution tools.
No special DeepSeek adapter is necessary. A plain chat without tools can reason
from the guidance but cannot claim to have executed checks. Installation into a
host's layout does not show that every model will follow the workflow equally well.

## Important gaps closed

| Gap | Change and evidence |
|---|---|
| Common project runners produced opaque evidence | Added fresh `jest-json`, `vitest-json` and generic `junit` adapters; named passes required, skipped/empty/stale/malformed results never count as success. |
| Report parsing could hide failures | Independent review reproduced negative JUnit counters cancelling an actual failure; a failing regression preceded nonnegative counter validation and non-cancelling failure aggregation. |
| Security was only a configured-check label | Repository now configures Gitleaks; CI explicitly provisions official 8.30.1 binaries with pinned SHA256 verification. Clean/finding/missing-tool controls exercise real behavior. No helper downloads tools implicitly. |
| License missing from installed code | The complete MIT notice now travels inside the installable package and is checked byte-for-byte. |
| Provider/host compatibility was vague | Documented model-versus-host distinction, capabilities, POSIX requirements, manual loading fallback, and concrete Codex/Claude Code/OpenCode installs. |
| Installation was assumed from folder structure | `skills@1.7.4` copied all 12 package files identically into three isolated project-local host layouts; installed verifier and reporter executed independently of repository source. |
| New validation dependency had an advisory | npm identified the unpatched `sprintf-js` precision-formatting advisory through Jest → Istanbul → js-yaml 3. A narrow override pins Istanbul's js-yaml to 4.3.2, removing that chain. Real YAML config loading and runner controls validate the changed API. |

The standard format permits a top-level `compatibility` string, but the bundled
older Skill Creator validator rejects it. Requirements therefore live in the
instruction body/README and arbitrary standard `metadata.compatibility`. This
avoids requiring a newer host parser; it is not advertised as automatic standard
compatibility-field discovery.

## Reproduced local evidence

On macOS with bundled Node 24.19.0 and Python 3.13:

- 55 Python runtime/harness/adapter regressions, no skips.
- Three named Node package, documentation, and entrypoint checks.
- Twelve real runner controls: Jest 30.5.2, Vitest 5.0.5 JSON, and Vitest-exported
  JUnit; each exercised actual passing, failing, skipped-only and setup-error runs.
  This validates the JUnit report contract, not every language's export wrapper.
- Three official CLI installation layouts, each running the installed helper.
- Real Gitleaks clean, synthetic canary, missing-tool and redaction controls;
  whole current-tree repository scan found no secrets under default rules.
- Pinned validation-runtime npm advisory scan: zero reported vulnerabilities at
  audit time. This is an advisory-service observation, not a vulnerability guarantee.
- 35 fixture tests across 12 projects; the thirteenth's intentionally broken import
  was identified separately. Five semantic before/after controls retained their
  expected assertion-failure/positive-execution distinction.
- Eight original-versus-revised verifier comparisons, 26 structural scenarios
  (10 with semantic oracles), skill validation and whitespace checks.

The initial sandbox fixture run could not bind loopback HTTP servers and failed;
rerunning the trusted fixtures with loopback permission restored the expected
results. Setup restrictions are not product regressions. No live infrastructure
or external model execution was used. Linux/macOS CI is configured; remote CI has
not been observed during this local task.

Commands are in README. Runtime acquisition and scanner acquisition are separate
explicit operations; all ordinary regressions run without package installation.
Installer smoke disables telemetry and isolates destinations/HOME. Synthetic
canaries are not live credentials. The final whole-tree check caught Python constant
folding an earlier synthetic canary into ignored bytecode; runtime generation now
avoids embedding that token, and the scanner remains unexcluded. Maintained scanning supplements the small
candidate scanner; contextual fixture decisions remain reviewed claims.

## Remaining limits and stopping decision

There is enough evidence for a useful public package, subject to remote CI after
publication. No further framework expansion is needed before that release.

- **Model effectiveness:** no controlled live Codex/Claude/DeepSeek campaign or
  improvement percentage is claimed. Collect real usage feedback before adding
  more rules. Tests cannot prove instruction adherence or assertion relevance.
- **Host/tool coverage:** helpers support POSIX process handling. Native Windows
  needs a suitable POSIX environment or direct project checks. Project-specific
  toolchains and wrappers must be provisioned and reviewed by their owners.
- **Security scope:** Gitleaks checks current-tree secrets; history, dependency
  risk, authorization, migrations and production recovery require relevant
  project checks and review. A generic skill cannot supply every application's
  threat model or credentials. Missing required checks stay inconclusive.
- **Trust boundary:** project commands and reports can lie or mutate their host;
  replay is not a malicious-code sandbox or cryptographic attestation.

The release step is to review/commit the complete local changes, push them to the
public source and observe the configured CI. Local installed copies still need a
whole-package update. No push, release or global installation was performed here.

The [Agent Skills specification](https://agentskills.io/specification) describes
package layout; the [official CLI](https://github.com/vercel-labs/skills) supports
multiple hosts. According to the [skills.sh FAQ](https://www.skills.sh/docs/faq),
leaderboard discovery follows users installing a public repository with the CLI.
There is no separate quality-certification claim. Installation telemetry, listing
timing, directory security review and remote host behavior are outside a local
smoke test's evidence.
