# Targeted high-risk review

Use for the changed trust boundaries and affected consumers. This is AI-assisted
review, not a penetration test or compliance certification. Record evidence,
prevention, tests, and residual risk for material findings. OWASP ASVS and NIST
SSDF are review maps, not evidence of compliance. Verify applicable editions and
requirements before making a standards mapping.

- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [NIST SSDF](https://csrc.nist.gov/projects/ssdf)

## Trust boundaries and data

Trace untrusted input to database, shell, filesystem, template, browser, and network
sinks. Review authentication separately from per-object/tenant authorization.
Check fail-closed behavior, session expiry, replay, error disclosure, dependency
risk, logs, and secret storage/rotation. A literal scanner match needs context;
a lack of matches does not establish a safe boundary.

Use the database driver's parameter-binding API for values. Allow-list dynamic
identifiers through the driver's supported identifier API; values and identifiers
are different contexts. Do not inspect runtime SQL for interpolation source syntax:
that syntax has already disappeared. Test malicious values through the real query
API and assert data/authorization behavior.
[SQL injection prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

Prefer framework escaping and safe DOM sinks. Output encoding depends on HTML text,
attribute, URL, JavaScript, or CSS context. Encoding a few HTML characters is not a
general `sanitizeHtml` function. Where rich HTML is required, use a maintained
sanitizer with an explicit policy and avoid unsafe post-sanitization transformations.
[XSS prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)

CSRF controls depend on credential transport and architecture. Prefer maintained
framework protections; review cookie authentication, SameSite constraints, origin
validation and token handling together. CORS is not authentication or a universal
CSRF defense. Public credential-free APIs may legitimately allow broad origins;
credentialed/private APIs need appropriate origin and access policies.
[CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

Use a maintained authentication system and password-hashing library with current
parameters suitable for the platform. Never copy toy password comparisons into
production. Privacy rights, retention, deletion, audit logging, and legal duties
depend on jurisdiction, purpose, and exceptions; an endpoint alone does not make
an application GDPR-compliant.

## Concurrency, retries, and idempotency

A cache get followed by set is not atomic. Model idempotency as a state machine:
atomically claim a scoped key with a unique constraint or provider-supported
primitive, bind it to a request fingerprint, distinguish in-progress/succeeded/
retryable failure, and persist success only with the successful effect. Define
crash recovery, leases/expiry, response replay, and key reuse behavior. If the
external effect cannot share a transaction, use provider idempotency or a durable
outbox/reconciliation design; do not promise exactly-once behavior from a helper.
Test concurrent duplicate requests and failures before/after the effect.

## Contracts and migrations

Review callers, consumers, rolling-version compatibility, defaults, nullability,
indexes/locks, data volumes, backfills, and partial failure. Prefer additive changes
and staged removal when old and new versions coexist. Rehearse on representative
isolated data. Choose a platform-specific recovery strategy: forward correction,
restore with known recovery point, or a proven reversible migration where valid.
A mandatory DOWN migration or round-trip can destroy data and is not universally
safe. Document irreversibility and validate backup restoration independently.

## Close the review

Recheck substantive fixes where the review found additional issues. Do not rerun
unchanged suites solely to fill phases. Fix introduced defects; report unrelated
pre-existing issues without silent scope expansion. Escalate consequential
unresolved risk to the authorized owner with concrete evidence and options.
