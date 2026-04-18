# Quick Change Walkthrough

## User Prompt
> "change the primary button color from blue to green"

## What Happens

### Mode Selection
- Risk: low.
- User language: no override.
- **Mode: Quick**.

### Quick Flow
- Read the button styling file.
- Confirm the change is a single-value cosmetic update with no behavior impact.
- Change the color token or literal.
- Run available checks.
- Present a one-line summary and stop for confirmation.

Example summary:

```text
Changed the primary button color from blue to green in Button.css. Verification: PASS. AI-reviewed, not human-audited.
```

If the work expands beyond that, Quick mode is no longer valid and the agent should promote to Standard immediately.
