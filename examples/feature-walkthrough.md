# Feature Walkthrough

## User Prompt
> "add a dark mode toggle to the settings page"

## What Happens

### Mode Selection
- Risk: MEDIUM (new UI component, state management, persistence)
- User language: no signal
- **Mode: Standard**

### Phase 1: Understand & Plan
- Scanned file tree, found `SettingsPage.jsx`, `SettingsPage.css`, `App.jsx`
- Checked for existing theme system: none found
- Checked available skills: found `frontend-design` skill — will delegate CSS work
- Implementation Brief:
  - Problem: Settings page has no dark mode toggle. Users want dark mode.
  - Acceptance criteria:
    1. Toggle switches between light and dark mode
    2. Preference persists across page reloads (localStorage)
    3. Respects system preference on first visit (prefers-color-scheme)
    4. No flash of wrong theme on page load
    5. Toggle is keyboard accessible
  - Files: SettingsPage.jsx, SettingsPage.css, App.jsx, new useTheme.js hook
  - Risk: CSS changes could affect other components if not scoped
- Plan: 4 steps

**Announce:** "Feature identified. Implementing 4 steps."

### Phase 2: Implement
- Created branch: `feat/dark-mode-toggle`
- Step 1: Created `useTheme.js` hook (reads localStorage → falls back to system pref → applies class to `<html>`)
- Step 2: Added toggle UI to `SettingsPage.jsx` with accessible switch
- Step 3: Added dark mode CSS variables in `SettingsPage.css` (delegated to frontend-design skill for palette)
- Step 4: Integrated hook in `App.jsx` to apply theme on mount (prevents flash)

**Announce:** "Implementation complete. Running checks."

### Phase 3: Gate & Test
- Linter/formatter: clean after auto-fix
- Existing tests: all pass
- Fix-guard-test-verify loop for the feature:
  - **Fix:** Feature implemented ✓
  - **Root cause:** N/A (new feature, not a bug)
  - **Guard:** Added fallback in useTheme — if localStorage throws (private browsing), defaults to system preference
  - **Tests:**
    - Toggle on/off changes theme class
    - Preference persists in localStorage
    - System preference respected on first visit
    - localStorage failure falls back gracefully
  - **Verify:** All new tests pass

**Announce:** "6 tests pass (4 new, 1 guardrail). Linting clean."

### Phase 4: Audit
**Pass 1 — Correctness:**
- All 5 acceptance criteria verified ✓
- Finding (BEHAVIORAL): Flash of wrong theme possible if JS loads slowly
  - Fix: Added inline `<script>` in HTML head to apply theme before render
  - Guard: Code comment explaining why this must be inline
  - Test: Test that theme class exists on `<html>` before React mounts
  - Verify: passes ✓

**Pass 2 — Security & Quality Checklist:**
- Accessibility: toggle is keyboard accessible with proper ARIA ✓
- Performance: no re-renders on theme change (CSS variables only) ✓
- Security: localStorage data is a string enum, no injection risk ✓
- 0 additional findings

**Announce:** "Audit done. 1 issue: fixed 1, guarded 1, tested 1."

### Phase 5: Regression & Final Verification
- Full test suite: all 7 pass (4 new, 2 guardrail, 1 existing)
- Guardrail completeness: localStorage fallback ✓, inline script comment ✓
- Updated: none (no API or config changes)

**Announce:** "All 7 tests pass. 2 guardrails verified."

### Phase 6: Ready Gate
```
What: Added dark mode toggle to settings page with localStorage
      persistence and system preference detection.
Files: useTheme.js (new), SettingsPage.jsx (toggle UI),
       SettingsPage.css (dark variables), App.jsx (theme init)
Tests: 4 new, 0 updated, 2 guardrail
Audit: 1 issue (theme flash) — fixed and guarded
Guardrails: localStorage error fallback, inline theme script comment
Commit: feat(settings): add dark mode toggle with persistence
Branch: feat/dark-mode-toggle
```

## Token Cost
~7,300 tokens total skill overhead (SKILL.md + self-verification.md at Ready Gate).
