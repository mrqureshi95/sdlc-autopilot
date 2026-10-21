# Pagination regression

Request: fix the first page skipping records.

Use Standard. Capture the starting state and identify the canonical pagination
function and callers. Write a named test for first/last/empty pages and observe the
reported off-by-one failure when practical. Fix the slice calculation and run the
affected scope. Inspect related patterns in context, triaging unrelated findings.

At handoff report the before/after observation, checks run, contract implications,
and limitations. A test count does not prove completeness; no extra rerun or
external model call is required just to fill a workflow phase.
