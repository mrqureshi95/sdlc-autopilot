# Measuring whether SDLC Autopilot adds value

Package tests show that helpers meet specific contracts. They do not show that
agents produce better projects. Installation counts show adoption. User reports
show experience. To measure improvement, collect outcomes and compare conditions.
This protocol is optional; the skill has no built-in usage telemetry or upload.

## Start with real work

For each ordinary task where recording is authorized, keep one short local record
using [the template](../evals/field-study/usage-record.template.json). Copy it outside
this public repository, replace the template marker, and complete the observed
fields after the task. Unknown values remain null, not zero or a presumed pass.
Capture the starting identity and exposure before work; do not reconstruct them
from a final green summary. Keep source, prompts and transcripts private unless
sharing is explicitly authorized. Pseudonyms and hashes can still be sensitive.

Record the task kind/risk, model and host versions, exact baseline commit and skill
revision/package digest. Record whether the skill was actually loaded, merely
installed, disabled, or unknown. Version 2.0.0 metadata identifies the release;
include the installed folder's complete file hash manifest for modified copies.

Have a reviewer inspect acceptance criteria and independently observed checks.
Record accepted/rework/rejected/inconclusive; corrective prompts; observed agent
elapsed minutes; human review/rework minutes; and any regression found during the
following seven days. Record the end of that follow-up window; a task observed
for only one day has not completed a seven-day check. Distinguish environment or
setup failures from behavioral failures without removing either from the record.
Do not invent time/cost from token counts, prose, or a guessed model price.

Existing Codex chats can supply retrospective examples when the owner authorizes
access. Record missing versions, unknown skill exposure and estimated timing as
unknown. A retrospective task without a reliable baseline is observational; it
cannot establish the skill caused the result. Do not automatically crawl unrelated
projects or private chats. This release creates no actual user-study records.

## Compare the same task under controlled conditions

Use isolated disposable snapshots, not risky experiments on production work.
A practical pilot is about ten representative tasks, each attempted both ways;
that is a debugging pilot, not a statistically powered proof. Expand only if the
pilot and intended claim justify the cost.

1. Before runs, freeze the tasks, starting commits, acceptance tests, rating rubric,
   budgets, exclusions and primary outcome. Include straightforward work and the
   boundary cases the skill is designed to handle. Reserve some hidden checks
   under evaluator control, outside the agent-editable workspace.
2. Keep model/version, host, tools, dependencies, permissions, task prompt and budget
   the same. Change only skill exposure. The control must not accidentally load a
   global/repository copy or inherited instructions from an earlier conversation.
   Use separate fresh sessions and isolated host configurations. Record unavoidable
   differences. Never disable ordinary project checks to create a weak control.
3. Randomize run order within each task pair. Use repeated attempts where feasible
   because models are variable; record repetitions rather than selecting the best
   output. Keep prior answers and fixes out of later runs' context.
4. A reviewer who does not know the condition evaluates patches and hidden checks
   against the frozen rubric. Preserve both versions and their evidence. Confirm
   meaningful assertion execution; self-reported completion is insufficient.
5. Retain every attempted run, including timeouts, tool failures and inconclusive
   results. Apply only the exclusion rules set beforehand and report exclusions
   with reasons. A skipped or missing run does not become a success.

The existing [scenario fixtures](../evals/evals.json) and
[semantic replay harness](../scripts/run-agent-evals.py) can validate collected
patches. They do not launch models or establish who produced a patch. Human
criteria stay separate. Only ten scenarios currently have semantic oracles;
review the others manually. Running supplied code requires a trusted patch or an
independently controlled sandbox; temporary folders are not adversarial isolation.
External-provider execution and any data transmission need their own authorization.

## Report outcomes, friction, and uncertainty

Use **independently accepted without material corrective rework within budget** as
a useful primary outcome. Define material rework and budget before comparing runs.
Report its count over all attempts and show inconclusive/excluded counts separately.
Also report independently verified behavior and defects as separate observations;
a helper pass alone is not task acceptance.

| Measure | What to report |
|---|---|
| Acceptance | Accepted-without-material-rework / all attempted runs, with numerator and denominator |
| Paired result | Tasks where only skill wins, only control wins, both pass, both fail, or unresolved |
| Defects | Reviewer-confirmed blocking defects and follow-up regressions, by severity and observation window |
| Human effort | Review/rework minutes and corrective prompts, including setup overhead |
| Delivery effort | Observed wall time and actual billed cost when available; missing measurements remain unknown |
| Workflow friction | Unnecessary tests, changes, permission pauses, scope expansion, and lost user edits |
| Uncertainty | Sample size, task mix, model/host versions, repeated-run variation, missingness and exclusions |

For paired outcomes report the task-level difference and appropriate uncertainty;
for time/effort show medians and spread as well as paired differences. Correlated
repetitions of one task are not independent extra tasks. Use statistical expertise
before making broad numerical superiority claims. Set the improvement and friction
thresholds before viewing results; do not invent a universal target afterward.

A useful result may be fewer defects or less human rework at similar elapsed time.
A result can also show no benefit or excessive overhead. Publish the full aggregate
comparison and limitations, rather than favorable anecdotes alone. Say “on these
tasks with this model/host” until broader evidence supports a wider claim.

## A reasonable operating habit

Use the released skill normally. Keep a lightweight optional record on selected
representative tasks and review the first batch for concrete failures or friction.
Run controlled comparisons on frozen tasks when making a public effectiveness
claim. Improve the skill only when results reveal a repeated, meaningful weakness.
No scheduled collection or model campaign is created by this protocol.
