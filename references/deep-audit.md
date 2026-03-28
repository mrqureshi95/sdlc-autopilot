# Deep Audit Reference

Loaded ONLY in full mode. Security checklists, guardrail patterns with code examples, API contract validation, migration guidance, convergence protocol.

## 1. Security Deep Dive Checklist

### OWASP Top 10 — AI Code Review Patterns

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

## 2. Guardrail Pattern Library

### Null/Undefined Protection
```typescript
// GUARD: Type narrowing utility
function assertDefined<T>(val: T | null | undefined, name: string): T {
  if (val == null) throw new Error(`${name} must be defined`);
  return val;
}
// TEST:
test('assertDefined throws on null', () => {
  expect(() => assertDefined(null, 'userId')).toThrow('userId must be defined');
});
test('assertDefined passes valid value', () => {
  expect(assertDefined('abc', 'userId')).toBe('abc');
});
```

### SQL Injection Prevention
```typescript
// GUARD: Rejects raw interpolation in SQL
function safeQuery(db: DB, sql: string, params: unknown[]) {
  if (sql.includes('${') || sql.includes("' +") || sql.includes('" +'))
    throw new Error('Raw interpolation in SQL — use parameterized queries');
  return db.query(sql, params);
}
// TEST:
test('safeQuery rejects interpolation', () => {
  const sql = `SELECT * FROM users WHERE id = '${userInput}'`;
  expect(() => safeQuery(db, sql, [])).toThrow('Raw interpolation');
});
```

### XSS Prevention
```typescript
// GUARD: Sanitize HTML — minimal entity encoding for simple text output.
// For rich HTML content, use a dedicated library (e.g., DOMPurify, sanitize-html).
function sanitizeHtml(input: string): string {
  return input.replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]!));
}
// TEST:
test('sanitizeHtml escapes script tags', () => {
  expect(sanitizeHtml('<script>alert(1)</script>')).not.toContain('<script>');
});
```

### Division by Zero
```typescript
// GUARD: Safe division
function safeDivide(a: number, b: number, fallback = 0): number {
  return b === 0 ? fallback : a / b;
}
// TEST:
test('safeDivide returns fallback on zero', () => {
  expect(safeDivide(10, 0)).toBe(0);
  expect(safeDivide(10, 0, -1)).toBe(-1);
});
```

### CSS Viewport Containment
```css
/* GUARD: Prevent elements hidden by virtual keyboards */
.input-container { position: sticky; bottom: 0; padding-bottom: env(safe-area-inset-bottom, 0px); }
```
```typescript
// TEST:
test('input visible with virtual keyboard', () => {
  window.innerHeight = 400;
  window.dispatchEvent(new Event('resize'));
  expect(screen.getByRole('searchbox').getBoundingClientRect().bottom).toBeLessThan(400);
});
```

### N+1 Query Prevention
```typescript
// GUARD: Query budget assertion
function assertQueryBudget(log: string[], max: number, ctx: string) {
  if (log.length > max) throw new Error(`${ctx}: ${log.length} queries > budget ${max}`);
}
// TEST:
test('stays within query budget', async () => {
  const queries: string[] = [];
  db.on('query', q => queries.push(q));
  await getUserList();
  assertQueryBudget(queries, 3, 'getUserList');
});
```

### CSRF Prevention
```typescript
// GUARD: CSRF token middleware for state-changing requests
function csrfProtection(req: Request, res: Response, next: NextFunction) {
  if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) return next();
  const token = req.headers['x-csrf-token'] || req.body._csrf;
  if (!token || token !== req.session?.csrfToken) {
    return res.status(403).json({ error: 'Invalid CSRF token' });
  }
  next();
}
// TEST:
test('rejects POST without CSRF token', async () => {
  const res = await request(app).post('/api/transfer').send({ amount: 100 });
  expect(res.status).toBe(403);
});
test('accepts POST with valid CSRF token', async () => {
  const agent = request.agent(app);
  const { body } = await agent.get('/api/csrf-token');
  const res = await agent.post('/api/transfer')
    .set('x-csrf-token', body.token).send({ amount: 100 });
  expect(res.status).not.toBe(403);
});
```

### Race Condition Prevention
```typescript
// GUARD: Idempotency key
async function withIdempotency(key: string, fn: () => Promise<void>) {
  if (await cache.get(`idempotent:${key}`)) return;
  await cache.set(`idempotent:${key}`, '1', { ex: 3600 });
  await fn();
}
// TEST:
test('duplicate requests ignored', async () => {
  let calls = 0;
  const fn = async () => { calls++; };
  await withIdempotency('req-1', fn);
  await withIdempotency('req-1', fn);
  expect(calls).toBe(1);
});
```

## 3. API Contract Validation

**Find callers:** `grep -rn "functionName\|/api/path" --include="*.ts"` (adapt extension per language)
**Check each caller:** correct arg types, handles new response shape, handles new errors, compiles if args changed.
**Guards:** API version header (`X-API-Version`), deprecation header, contract tests (request shape → response shape), old-shape test → graceful error.

## 4. Database Migration Guidance

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

## 5. Convergence Pass 3 Protocol

Re-review ALL changes from passes 1-2 for structural completeness.

**Categorization:** Structural (code impact if recurring) → MUST have guard+test. Behavioral (user impact) → SHOULD have guard+test. Cosmetic → fix sufficient.

**For each structural finding verify:**
- [ ] Fix present and correct
- [ ] Guardrail exists (type/linter/assertion/test/comment)
- [ ] Guardrail test exists and passes
- [ ] Root cause scan performed, other occurrences addressed

**Retry:** Max 3 cycles per finding. If unresolved → escalate to user with: what was found, what was attempted, why auto-fix failed, recommended manual fix.
