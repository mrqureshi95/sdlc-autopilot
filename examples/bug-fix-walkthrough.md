# Bug Fix Walkthrough

## User Prompt
> "the search field gets hidden behind the keyboard on mobile"

## What Happens

### Mode Selection
- Risk: medium.
- User language: no override.
- **Mode: Standard**.

### Phase 1: Understand
- Read the relevant UI files and identify the layout bug.
- Root-cause hypothesis: bottom-positioned input does not adapt to viewport shrink when the virtual keyboard appears.
- Acceptance criteria:
  1. Search field stays visible when the keyboard opens.
  2. It does not overlap surrounding content.
  3. The fix still behaves on mobile browsers that expose `visualViewport`.
- Edge cases captured up front: safe-area inset, resize timing, and fallback when `visualViewport` is unavailable.

### Phase 2: Implement
- Prefer a failing reproducer first if the existing harness can model the viewport behavior.
- Change the positioning strategy so the input follows the visible viewport instead of the page bottom.
- Keep the fix localized to the affected surface.

### Phase 3: Verify
- Run lint and existing tests.
- Apply Fix-Guard-Test-Verify:
  - **Fix:** change the layout behavior.
  - **Root cause scan:** search for the same bottom-input pattern elsewhere and only fix confirmed matches.
  - **Guard:** add the smallest effective protection, such as shared positioning logic or an invariant around viewport-driven placement.
  - **Test:** add a regression test that would fail before the fix and an edge-case test for fallback behavior.
  - **Verify:** rerun the affected tests.
- Review the full diff for correctness, accessibility, and source-of-truth drift.

### Phase 4: Ready Gate
Show the raw output of `scripts/verify-pipeline.sh standard`, then summarize:

```text
What: Fixed the mobile keyboard overlap bug for the search field.
Tests: regression test for viewport overlap, edge-case coverage for fallback behavior.
Guardrails: shared bottom-input handling to reduce recurrence.
Root cause scan: searched for the same pattern in sibling components; fixed only confirmed matches.
Limitations: AI-assisted review — catches known patterns, not novel vulnerabilities.
```

If another model is available, run an adversarial review there. Otherwise generate the copyable prompt.

### Phase 5: Ship
Wait for explicit confirmation, then commit and push.
