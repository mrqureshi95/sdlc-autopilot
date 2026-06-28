# Deep Audit Reference — AI-Assisted Security Review

Loaded ONLY in full mode. Security checklists, guardrail patterns with code examples, API contract validation, migration guidance, convergence protocol.

**Scope and limitations:** This is an AI-assisted review using known vulnerability patterns. It is NOT a professional penetration test, security audit, or expert human review. It can catch KNOWN patterns (OWASP Top 10 signatures, common anti-patterns, obvious misconfigurations, some straightforward concurrency mistakes). It CANNOT catch novel attack vectors, complex business logic flaws, subtle or distributed race conditions, subtle cryptographic errors, or context-dependent vulnerabilities that require full-system understanding. For HIGH-RISK domains (auth, payments, PII, crypto), always recommend expert human review in the change summary.

## 1. Standards Anchors

Use these standards as a review map, not as a compliance claim.

- OWASP Application Security Verification Standard (ASVS) 5.0.0: https://owasp.org/www-project-application-security-verification-standard/
- NIST Secure Software Development Framework (SSDF) SP 800-218 v1.1: https://csrc.nist.gov/pubs/sp/800/218/final

Full-mode security findings should record:

1. **ASVS area:** the closest relevant ASVS 5.0.0 area.
2. **SSDF group:** PO, PS, PW, or RV.
3. **Evidence:** changed file, route, function, config, or test that proves the issue was addressed.
4. **Guardrail:** type, validator, middleware, invariant, static rule, or test that reduces recurrence.
5. **Residual risk:** anything not covered by AI-assisted review.

Never claim ASVS or SSDF compliance unless a qualified human-led assessment actually happened.

### Fast ASVS / SSDF Mapping

| Review target | ASVS 5.0.0 area | NIST SSDF group |
|---|---|---|
| XSS, unsafe HTML, unsafe encoding | V1 Encoding and Sanitization; V3 Web Frontend Security | PW Produce Well-Secured Software |
| Input validation, business rules, abuse cases | V2 Validation and Business Logic; V15 Secure Coding and Architecture | PW Produce Well-Secured Software |
| API routes, web services, request/response contracts | V4 API and Web Service | PW Produce Well-Secured Software |
| Uploads, downloads, path traversal, file type validation | V5 File Handling | PW Produce Well-Secured Software |
| Login, MFA, credentials, password reset | V6 Authentication | PW Produce Well-Secured Software; PS Protect the Software |
| Cookies, session expiry, token storage | V7 Session Management | PW Produce Well-Secured Software; PS Protect the Software |
| Authorization, RBAC, object ownership | V8 Authorization | PW Produce Well-Secured Software |
| JWTs and other self-contained tokens | V9 Self-contained Tokens | PW Produce Well-Secured Software; PS Protect the Software |
| OAuth, OIDC, delegated auth | V10 OAuth and OIDC | PW Produce Well-Secured Software |
| Crypto algorithms, key handling, hashing | V11 Cryptography | PS Protect the Software; PW Produce Well-Secured Software |
| TLS, service-to-service communication | V12 Secure Communication | PS Protect the Software |
| Runtime configuration, CORS, headers, debug settings | V13 Configuration | PO Prepare the Organization; PW Produce Well-Secured Software |
| PII, retention, masking, privacy controls | V14 Data Protection | PS Protect the Software; PW Produce Well-Secured Software |
| Supply chain, dependencies, provenance | V15 Secure Coding and Architecture | PS Protect the Software; PO Prepare the Organization |
| Logging, monitoring, error handling, incident clues | V16 Security Logging and Error Handling | RV Respond to Vulnerabilities; PW Produce Well-Secured Software |
| WebRTC media/data channels | V17 WebRTC | PW Produce Well-Secured Software |

NIST SSDF groups used here:

- **PO Prepare the Organization:** people, process, and technology are ready for secure development.
- **PS Protect the Software:** protect code, components, and release artifacts from tampering or unauthorized access.
- **PW Produce Well-Secured Software:** design, implement, test, and release software with fewer vulnerabilities.
- **RV Respond to Vulnerabilities:** identify, fix, and prevent recurrence of residual vulnerabilities.

## 2. Security Deep Dive Checklist

### ASVS-Mapped AI Code Review Patterns

**A01 Broken Access Control** — Grep: `role|permission|isAdmin|canAccess|authorize|middleware` — Verify every endpoint checks auth AND authz. No direct object refs without ownership. Guard: deny-by-default middleware.

**A02 Cryptographic Failures** — Grep: `md5|sha1|encrypt|hash|password|token|jwt` — No weak hashing (MD5/SHA1), no hardcoded secrets. Passwords use bcrypt/scrypt/argon2. Guard: crypto wrapper enforcing approved algorithms.

**A03 Injection** — JS/TS: `eval\(|innerHTML|dangerouslySetInnerHTML|\.query\(` — Python: `pickle\.loads|exec\(|eval\(|subprocess.*shell=True|cursor\.execute.*%` — SQL: `SELECT.*\+|INSERT.*\+|".*\$\{.*\}.*FROM` — Guard: parameterized queries, input sanitization, CSP.

**A04 Insecure Design** — Rate limiting on auth, account lockout, no business logic bypasses. Guard: validation at trust boundaries.

**A05 Misconfiguration** — Grep: `cors|CORS|Access-Control|helmet|csrf` — CORS not `*` in prod, debug off. Guard: security header middleware.

**A06 Vulnerable Components** — Run `npm audit` / `pip audit`. No known CVEs. Guard: lockfile + audit in CI.

**A07 Auth Failures** — Grep: `session|cookie|localStorage.*token|bearer` — Tokens httpOnly+secure+sameSite, JWT has expiry. Guard: auth utility with secure defaults.

**A08 Data Integrity** — No unsigned deserialization of untrusted data. Guard: schema validation on external data.

**A09 Logging** — Auth failures logged, sensitive data NOT logged. Grep: `console\.log.*password|logging.*token` — Guard: structured logger with redaction.

**A10 SSRF** — Grep: `fetch\(|axios\(|requests\.get\(` — User URLs validated against allowlist. Guard: URL validation utility.

### Auth Flow Verification
1. Trace: login → token creation → storage → validation → protected route
2. Verify: no leakage, proper expiry/revocation, role checks on operations not just pages
3. Test: unauthenticated → 401, unauthorized → 403

### Data Handling
PII encrypted at rest, masked in logs. No PII in error messages. GDPR: deletion + export endpoints. Guard: PII markers + log sanitizer.

## 3. Guardrail Pattern Library

### Null/Undefined Protection
```typescript
function assertDefined<T>(val: T | null | undefined, name: string): T {
  if (val == null) throw new Error(`${name} must be defined`);
  return val;
}
// Test: assertDefined(null, 'userId') → throws; assertDefined('abc', 'userId') → 'abc'
```

### SQL Injection Prevention
```typescript
function safeQuery(db: DB, sql: string, params: unknown[]) {
  if (sql.includes('${') || sql.includes("' +") || sql.includes('" +'))
    throw new Error('Raw interpolation in SQL — use parameterized queries');
  return db.query(sql, params);
}
// Test: safeQuery(db, `SELECT * WHERE id = '${input}'`, []) → throws
```

### XSS Prevention
```typescript
// For rich HTML, use DOMPurify or sanitize-html instead
function sanitizeHtml(input: string): string {
  return input.replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]!));
}
// Test: sanitizeHtml('<script>alert(1)</script>') → no <script> tag
```

### Division by Zero
```typescript
function safeDivide(a: number, b: number, fallback = 0): number {
  return b === 0 ? fallback : a / b;
}
// Test: safeDivide(10, 0) → 0; safeDivide(10, 0, -1) → -1
```

### CSS Viewport Containment
```css
.input-container { position: sticky; bottom: 0; padding-bottom: env(safe-area-inset-bottom, 0px); }
```
```typescript
// Test: resize to 400px height → searchbox bottom < 400
```

### N+1 Query Prevention
```typescript
function assertQueryBudget(log: string[], max: number, ctx: string) {
  if (log.length > max) throw new Error(`${ctx}: ${log.length} queries > budget ${max}`);
}
// Test: track queries during getUserList() → assertQueryBudget(queries, 3, 'getUserList')
```

### CSRF Prevention
```typescript
function csrfProtection(req: Request, res: Response, next: NextFunction) {
  if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) return next();
  const token = req.headers['x-csrf-token'] || req.body._csrf;
  if (!token || token !== req.session?.csrfToken)
    return res.status(403).json({ error: 'Invalid CSRF token' });
  next();
}
// Test: POST without token → 403; POST with valid token → not 403
```

### Race Condition Prevention
```typescript
// Use for obvious duplicate-request or idempotency gaps; not proof against subtle concurrency bugs.
async function withIdempotency(key: string, fn: () => Promise<void>) {
  if (await cache.get(`idempotent:${key}`)) return;
  await cache.set(`idempotent:${key}`, '1', { ex: 3600 });
  await fn();
}
// Test: call twice with same key → fn runs once
```

## 4. API Contract Validation

**Find callers:** `grep -rn "functionName\|/api/path" --include="*.ts"` (adapt extension per language)
**Check each caller:** correct arg types, handles new response shape, handles new errors, compiles if args changed.
**Guards:** API version header (`X-API-Version`), deprecation header, contract tests (request shape → response shape), old-shape test → graceful error.

## 5. Database Migration Guidance

**Create:** `YYYYMMDDHHMMSS_description.sql` with UP and DOWN. Non-destructive: nullable first, backfill, then constrain.
**Test:** `migrate up && migrate down && migrate up` — DB unchanged after round-trip.
```typescript
test('migration is reversible', async () => {
  const before = await getSchemaSnapshot();
  await migrateUp(); await migrateDown();
  expect(await getSchemaSnapshot()).toEqual(before);
});
test('schema matches snapshot', async () => {
  expect(await getSchemaSnapshot()).toMatchSnapshot();
});
```
**Rollback:** Keep down migration tested. Backup before data migrations. Deprecate columns before removal.

## 6. Convergence Pass Protocol

Re-review ALL changes from passes 1-2 for structural completeness.

**Categorization:** Structural (code impact if recurring) → MUST have guard+test. Behavioral (user impact) → SHOULD have guard+test. Cosmetic → fix sufficient.

**For each structural finding verify:**
- [ ] Fix present and correct
- [ ] Guardrail exists (type/linter/assertion/test/comment)
- [ ] Guardrail test exists and passes
- [ ] Root cause scan performed, other occurrences addressed

**Retry:** Max 3 cycles per finding. If unresolved → escalate to user with: what was found, what was attempted, why auto-fix failed, recommended manual fix.
