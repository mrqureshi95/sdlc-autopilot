# Bug Fix Walkthrough

## User Prompt
> "the search field gets hidden behind the keyboard on mobile"

## What Happens

### Mode Selection
- Risk: MEDIUM (bug fix, UI component)
- User language: no signal
- **Mode: Standard**

### Phase 1: Understand & Plan
- Grepped for "search" → found `SearchPage.jsx`, `SearchPage.css`
- Read both files: search input uses `position: absolute; bottom: 20px`
- Root cause hypothesis: absolute positioning doesn't account for virtual keyboard reducing viewport
- Acceptance criteria:
  1. Search field visible when virtual keyboard is open
  2. Search field doesn't overlap other content
  3. Works on iOS and Android
- Plan: 2 steps — fix CSS positioning, add resize listener

**Announce:** "Bug fix identified. Implementing 2 steps."

### Phase 2: Implement
- Created branch: `fix/search-keyboard-overlap`
- Changed `position: absolute` to `position: sticky; bottom: 0`
- Added `padding-bottom: env(safe-area-inset-bottom)` for safe area
- Added `visualViewport` resize handler to scroll input into view

**Announce:** "Implementation complete. Running checks."

### Phase 3: Gate & Test
- Linter/formatter: clean
- Existing tests: pass
- Fix-guard-test-verify loop:
  - **Fix:** ✓ in place
  - **Root cause:** Grepped `position: absolute.*bottom` — found same pattern in `ChatInput.css`. Fixed that too.
  - **Guard:** Added CSS comment: `/* WARNING: Use position:sticky, not absolute, for inputs near viewport bottom — virtual keyboards reduce viewport */`
  - **Test:** Wrote regression test simulating viewport resize
  - **Verify:** New test passes

**Announce:** "4 tests pass (2 new, 1 guardrail). Linting clean."

### Phase 4: Audit
**Pass 1 — Correctness:**
- All 3 acceptance criteria met ✓
- No logic errors, no race conditions
- 0 findings

**Pass 2 — Quick security scan (convergence shortcut — pass 1 was clean):**
- No security issues in CSS changes
- 0 findings

**Announce:** "Audit done. 0 issues."

### Phase 5: Regression & Final Verification
- Full test suite: all pass
- Guardrail completeness: CSS comment in place, regression test passes
- No docs to update

**Announce:** "All 4 tests pass. 1 guardrail verified."

### Phase 6: Ready Gate
```
What: Fixed search field being hidden behind virtual keyboard on mobile.
      Also fixed same pattern in ChatInput.css.
Files: SearchPage.css (sticky positioning), ChatInput.css (same fix)
Tests: 2 new (viewport resize regression), 0 updated, 1 guardrail
Audit: 0 issues
Root cause: position:absolute pattern found in 1 other location (fixed)
Guardrails: CSS comment warning against absolute positioning for bottom inputs
Commit: fix(search): prevent keyboard overlap on mobile search field
Branch: fix/search-keyboard-overlap
```

## Token Cost
~2,500 tokens total skill overhead.
