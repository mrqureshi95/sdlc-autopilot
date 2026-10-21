# Optional local usefulness records

This directory ships a template only, with no study results or automatic logger.
See [the measurement protocol](../../docs/measuring-value.md).

Copy `usage-record.template.json` outside this public repository and set
`is_template` to false only when recording an actual authorized attempt. Never
aggregate a template as a run. Keep unknown measurements null. Use:

- `study_kind`: observational, retrospective, or controlled-paired.
- `condition`: skill-loaded, skill-disabled, or unknown. Installed alone is unknown.
- `task_kind`: bug-fix, feature, refactor, review, cosmetic, or other.
- `risk`: quick, standard, full, or unknown.
- `reviewer_acceptance`: accepted, rework, rejected, or inconclusive.
- `independent_behavior_check`: pass, fail, inconclusive, or not-applicable.

Use a shared `pair_id` only for attempts of the same frozen task under comparable
conditions. Every repetition gets its own record. Boolean observations use actual
true/false or null. Counts/minutes are nonnegative observed numbers or null.
`workflow_friction` can be a short redacted note; paths in `evidence` refer to local
artifacts, not permission to upload those artifacts. Actual cost must include its
currency and measurement source. Follow-up regressions stay null until checked;
record the actual observation period even when shorter than seven days.

Do not commit task records, private project names, prompts, transcripts, credentials
or source patches here. Share only explicitly approved redacted aggregates. This
is a manually completed data template, not an attestation or validated schema.
