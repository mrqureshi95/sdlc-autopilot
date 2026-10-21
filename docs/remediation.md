# Audit remediation ledger

Scope: local package remediation on `codex/audit-remediation`, starting from a clean
`6c1e8d1d8ea004a7398377005c71c09c516d14e7`. No installed skill copy, live deployment,
external-model review, push, or release is part of this work. The initial clean Git
state was observed; the new snapshot helper did not yet exist, so this task has no
helper-generated task-start snapshot. Do not reconstruct one after the fact.

## Finding disposition

| Audit group | Disposition and implementation | Evidence / limits |
|---|---|---|
| 1. All-skipped Full success; hidden committed branch changes | Replaced the shell verifier with structured evidence states and a Python implementation. Full outside Git is inconclusive. Base selection is explicit or a reported local merge-base, never conditional on an empty working diff. Net branch/worktree/untracked evidence uses NUL-delimited paths. | Runtime regressions cover README masking, filenames with spaces, subdirectories, linked worktrees, renames/deletions, and untracked files. Net diff is not historical commit scanning. |
| 1. Ownership/provenance | Added external task-start hash snapshots, exact base/head/cwd/commands and digests, and path-level pre-existing/mixed/changed/unknown attribution. | Mixed hunks still require review; hashes are not signed authorship attestations. |
| 2. Filename/test/assertion/coverage false confidence | Removed assertion/guardrail token counts, test-churn requirements and stale coverage consumption. Narrow Node fallback requires named runner events, not file wrappers. Explicit pytest/unittest adapters measure fresh positive counts. | Tests cover latest_data.js, empty modules, failing spaced paths, deleted tests, existing unchanged tests and stale same-basename coverage. Quality and completeness remain human judgments. |
| 2. Weak secret scans and suppressions | Whole current changed text scan with content-free locations/fingerprints; no test/config/example exemption. Added common provider/private-key candidates and exact contextual review decisions. | This is a candidate scan, not a maintained security scanner. Full behavioral evidence requires a configured security command; missing tooling stays inconclusive. Ignored/binary/oversize/symlink paths and history remain explicit limits. |
| 2. Unsound strict inversion | Intentionally removed automatic inversion. Compatibility entrypoint exits 2 and explains isolated before/after evidence. | Dependency-complete runner-aware generic inversion is deferred: supporting arbitrary runners soundly would require a larger trusted execution system. No unsupported guarantee remains. |
| 3. Mutating gates, downloads, missing macOS timeout | Replaced implicit repo-wide fixes/npx with inspected explicit project commands and separate file-scoped fix adapters. Python bounds all commands and cleans process groups on POSIX. | Regressions cover missing executables and macOS timeout without GNU timeout. Configured commands are executable code, not sandboxed or guaranteed non-mutating. |
| 3. Polyglot/monorepo/toolchain drift and installed paths | Detect lists all manifests present and configured/available/unverified commands; repeated explicit project scopes use canonical wrappers. Shell wrappers resolve siblings from installation. | Automatic universal discovery is intentionally replaced with explicit configuration. Java/Ruby/Rust installation compatibility is not demonstrated runtime behavior. |
| 4. Unsafe SQL/idempotency/HTML/CSRF recipes | Removed copy-paste pseudo-controls. Guidance now uses parameter APIs, framework/context-aware controls, atomic state semantics and tested recovery requirements. | Official OWASP references; no bundled pseudo-sanitizer or runtime interpolation detector remains. |
| 4. CORS/password/privacy/migrations overreach | Qualified architecture/platform/jurisdiction assumptions. Standards mappings are optional review aids, never compliance claims. | No mandatory DOWN/round-trip or endpoint-equals-GDPR claim remains. |
| 5. Unsafe deployment/recovery commands | Replaced generic recipes with exact identity/revision/environment, preview/plan, health and authorized recovery workflow. History repair is distinguished from SQL recovery. Removed prune/stack-delete/stop-port/stash/rebase routines. | Official Supabase, Docker, Vercel and AWS sources checked. Netlify remains a help/docs lookup, without an unverified rollback command. Tests use only local fixtures/mocks; no deployment validity claim. |
| 6. Confidentiality and instruction hierarchy | External-provider review is opt-in by destination/payload; both diff sides/context need redaction and size cap. No automatic full-diff prompt. Repository/diff/tool instructions are untrusted data. Host hierarchy and user scope are respected. | Local forward review used no external provider. Redaction cannot guarantee confidentiality; final payload inspection remains necessary. |
| 7. Review path, risk and ceremony | Separate task type from exposure/blast radius/reversibility/contract risk. Cosmetic multi-file/security-adjacent work is proportional. Existing authorization persists; no compulsory ship or repeated approval. | Independent local forward test confirms clean Full review executes no project commands. |
| 7. Test intent, repetition, scope and user work | Match regression/characterization/contracts/rehearsal/benchmarks to task. Allow deterministic seams. Repeat checks only for new evidence needs. Fix introduced issues, triage unrelated findings, preserve edits on cancel. | Removed arbitrary reverts, universal test inversion, giant matrices and automatic scope expansion. Behavioral agent adherence remains partially unmeasured. |
| 8. Structural evaluation marketed as behavior | Removed metadata-flag/summary/verifier-string success checks. Separate structure, semantic replay, text presence and pending human criteria. Missing negative-check transcripts are inconclusive. | Harness schema/provenance/cleanup/negative tests; no invented pass rate or speed statistics. |
| 8. Reproducible executable evaluation | Central exact-pinned npm runtime/lockfile, separate preparation with lifecycle scripts disabled, no installs during replay, disposable workspaces, sanitized environment, bounded processes. Evaluator-owned oracles for a subset. | Temporary directories are not an OS sandbox. Malicious-agent campaigns require external isolation; no external agent campaign has been run. |
| 8. Broken fixtures and mismatched requests | Replaced undeclared CRA/Jest dependency setup with locked Vitest runtime, fixed test import, used Node SQLite to avoid unbuilt native modules, and aligned prompts/criteria with code, risk and scope. | Baseline tests run separately from planted-defect semantic controls. Mobile keyboard layout still needs real-browser/device judgment, not jsdom claims. |
| 8. Docs/release drift | Rewrote current README/GUIDANCE/browser overview/examples/evidence page, kept historical Git/release history, and updated CI to run substantive checks on Linux/macOS. | Local macOS evidence only; configured CI jobs have not been observed running remotely. Installed copies remain unchanged until whole-package reinstall. |

## Critical re-audit

The independent forward test exercised a real before/after Node regression with
pre-existing user work and a clean read-only Full review. It found malformed-config
tracebacks, inconsistent detection status and empty-scan wording. Regression tests
were added and these findings were corrected. A fresh critical re-audit then found
expected-failure counts, an oracle stdout impersonation, stale-context decisions,
ancestor-symlink traversal, malformed baselines, mode-only attribution, and omitted
new-file provenance. These were reproduced with failing tests and corrected.
Oracle completion records now reject early exits/stdout markers; in-process hostile
code remains outside the trusted replay contract, with independent sandboxing
required for malicious-agent evaluation.

Final runtime, fixture, semantic-control, package, syntax and diff checks are recorded
in [empirical-results.md](../evals/empirical-results.md). Remaining limits are explicit
replacements/deferments above, not passed claims. This package is suitable for local
trial with reviewed commands; it does not establish autonomous production safety.

The final independent bounded confirmation re-ran each material reproduction and
confirmed correct counts, structured errors, added-path provenance, early-exit
handling, context invalidation, symlink exclusion, mode attribution and cleanup.
Snapshot artifacts also use owner-only permissions even under a permissive umask.
No material mismatch remained in that confirmation. Broader behavior and production
safety remain outside the locally demonstrated evidence.

A subsequent user-requested full re-audit found and fixed additional scope,
provenance, TODO-handling and documentation gaps; see [the follow-up audit](re-audit.md).
The original observations above describe that earlier local revision.
