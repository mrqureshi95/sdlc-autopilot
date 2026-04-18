# Feature Walkthrough

## User Prompt
> "add a dark mode toggle to the settings page"

## What Happens

### Mode Selection
- Risk: medium.
- User language: no override.
- **Mode: Standard**.

### Phase 1: Understand
- Read the settings UI, the app shell, and any existing preference storage.
- Identify the canonical source of truth for theme state before adding anything new.
- Capture acceptance criteria:
  1. Toggle changes theme.
  2. Preference persists.
  3. System preference is respected on first load.
  4. The toggle is accessible.
  5. No flash of the wrong theme on load.
- Note relevant edge cases: storage failure, first visit, SSR or pre-render timing, and keyboard interaction.

### Phase 2: Implement
- Delegate styling specifics to a frontend skill if one is installed.
- Add the smallest safe theme abstraction instead of duplicating logic across components.
- Keep theme persistence and theme application tied to one source of truth.

### Phase 3: Verify
- Run the existing checks.
- Apply Fix-Guard-Test-Verify to feature risks and any findings discovered during review:
  - Guard against storage failures.
  - Test on, off, persistence, system-preference fallback, and first-load behavior.
  - Review the full diff for accessibility, performance, and source-of-truth drift.
- If a flash-of-incorrect-theme issue is discovered during verification, fix it there rather than deferring it to a separate ceremonial audit phase.

### Phase 4: Ready Gate
Show the raw verifier output, then summarize:

```text
What: Added a dark-mode toggle with persistent preference handling.
Tests: toggle behavior, persistence, first-load preference, storage-failure fallback, accessibility coverage.
Guardrails: shared theme source of truth and failure fallback behavior.
Deferred risks: none, or list them explicitly.
Limitations: AI-assisted review — catches known patterns, not novel vulnerabilities.
```

If another model is available, use it for adversarial review. Otherwise generate the copyable prompt.

### Phase 5: Ship
Wait for user confirmation, then commit and push.
