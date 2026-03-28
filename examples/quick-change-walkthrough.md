# Quick Change Walkthrough

## User Prompt
> "change the primary button color from blue to green"

## What Happens

### Mode Selection
- Risk: LOW (color/style change)
- User language: no signal
- **Mode: Quick**

### Phase 1: Understand
- Read `src/Button.css` — found `.btn-primary { background-color: #2563eb; }`
- Read `src/Button.jsx` — confirms it uses the CSS class
- Change is clear: update the hex color value

### Phase 2: Implement
- Changed `#2563eb` (blue) to `#16a34a` (green) in `Button.css`
- Fix-guard-test loop (lightweight): fix applied, no guardrail needed (cosmetic)

### Phase 3: Verify
- Ran ESLint → clean
- Ran Prettier → auto-formatted
- Ran existing tests → all pass
- Quick check: no other files reference the hex value directly

### Phase 4: Ship
**Summary:** "Changed primary button color from blue (#2563eb) to green (#16a34a) in Button.css. Tests pass."

User says "ship it" → committed as `style(button): change primary color from blue to green`

## Token Cost
~4,900 tokens total skill overhead (SKILL.md only). No audit passes. No reference files loaded.
