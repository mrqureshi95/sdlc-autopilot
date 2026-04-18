#!/bin/sh
# run-evals.sh — Validate eval fixture STRUCTURE (directories exist, JSON valid, files present).
# Does NOT run the skill against fixtures or verify assertions.
# Assertions in evals.json are human-verifiable criteria for manual evaluation.
# To evaluate the skill itself, run each scenario with an AI agent and check assertions manually.
# POSIX-compatible.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
EVALS_JSON="$ROOT_DIR/evals/evals.json"
FIXTURES_DIR="$ROOT_DIR/evals/fixtures"

# Use temp files for counters (POSIX subshell workaround)
COUNTER_FILE=$(mktemp)
echo "0 0 0" > "$COUNTER_FILE"
trap 'rm -f "$COUNTER_FILE"' EXIT

inc_pass() {
  read p f w < "$COUNTER_FILE" || true
  echo "$((p + 1)) $f $w" > "$COUNTER_FILE"
  printf "  ✓ %s\n" "$1"
}
inc_fail() {
  read p f w < "$COUNTER_FILE" || true
  echo "$p $((f + 1)) $w" > "$COUNTER_FILE"
  printf "  ✗ %s\n" "$1"
}
inc_warn() {
  read p f w < "$COUNTER_FILE" || true
  echo "$p $f $((w + 1))" > "$COUNTER_FILE"
  printf "  ⚠ %s\n" "$1"
}

# --- Check evals.json exists and is valid JSON ---
printf "=== Validating evals.json (fixture structure only — assertions require manual evaluation) ===\n"
if [ ! -f "$EVALS_JSON" ]; then
  inc_fail "evals.json not found at $EVALS_JSON"
  printf "\n=== Cannot continue without evals.json ===\n"
  exit 1
fi

if command -v python3 >/dev/null 2>&1; then
  if python3 -c "import json; json.load(open('$EVALS_JSON'))" 2>/dev/null; then
    inc_pass "evals.json is valid JSON"
  else
    inc_fail "evals.json is NOT valid JSON"
    exit 1
  fi
elif command -v node >/dev/null 2>&1; then
  if node -e "JSON.parse(require('fs').readFileSync('$EVALS_JSON','utf8'))" 2>/dev/null; then
    inc_pass "evals.json is valid JSON"
  else
    inc_fail "evals.json is NOT valid JSON"
    exit 1
  fi
else
  inc_warn "No JSON validator available (python3 or node). Skipping JSON validation."
fi

# Extract eval data using available tools
if command -v python3 >/dev/null 2>&1; then
  EVAL_COUNT=$(python3 -c "
import json
data = json.load(open('$EVALS_JSON'))
print(len(data.get('evals', [])))
")
  EVAL_IDS=$(python3 -c "
import json
data = json.load(open('$EVALS_JSON'))
for e in data.get('evals', []):
    print(e['id'], e['name'], e.get('fixture', ''), e['expected_mode'], len(e.get('assertions', [])))
")
elif command -v node >/dev/null 2>&1; then
  EVAL_COUNT=$(node -e "
const d = JSON.parse(require('fs').readFileSync('$EVALS_JSON','utf8'));
console.log(d.evals.length);
")
  EVAL_IDS=$(node -e "
const d = JSON.parse(require('fs').readFileSync('$EVALS_JSON','utf8'));
d.evals.forEach(e => console.log(e.id, e.name, e.fixture||'', e.expected_mode, (e.assertions||[]).length));
")
else
  inc_fail "No JSON parser available (python3 or node)"
  exit 1
fi

printf "  Found %s eval(s)\n\n" "$EVAL_COUNT"

# --- Validate each eval ---
printf "=== Validating fixtures ===\n"
echo "$EVAL_IDS" | while IFS=' ' read -r id name fixture mode assertion_count; do
  [ -z "$id" ] && continue
  printf "\n[Eval %s: %s] (mode: %s, assertions: %s)\n" "$id" "$name" "$mode" "$assertion_count"

  # Check mode is valid
  case "$mode" in
    quick|standard|full) inc_pass "Valid mode: $mode" ;;
    *) inc_fail "Invalid expected_mode: $mode" ;;
  esac

  # Check assertions exist
  if [ "$assertion_count" -gt 0 ]; then
    inc_pass "Has $assertion_count assertion(s)"
  else
    inc_fail "No assertions defined"
  fi

  # Check fixture directory exists (if specified)
  if [ -z "$fixture" ]; then
    inc_warn "No fixture directory specified"
    continue
  fi

  FIXTURE_PATH="$ROOT_DIR/evals/$fixture"
  if [ -d "$FIXTURE_PATH" ]; then
    inc_pass "Fixture directory exists: $fixture"
  else
    inc_fail "Fixture directory MISSING: $fixture"
    continue
  fi

  # Count files in fixture
  FILE_COUNT=$(find "$FIXTURE_PATH" -type f | wc -l | tr -d ' ')
  if [ "$FILE_COUNT" -gt 0 ]; then
    inc_pass "Fixture has $FILE_COUNT file(s)"
  else
    inc_fail "Fixture directory is empty"
  fi

  # Check for source files
  SRC_COUNT=$(find "$FIXTURE_PATH" -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.html" -o -name "*.css" \) | wc -l | tr -d ' ')
  if [ "$SRC_COUNT" -gt 0 ]; then
    inc_pass "Has $SRC_COUNT source file(s)"
  else
    inc_warn "No recognized source files found"
  fi

  # Check for test files if mode is standard or full
  if [ "$mode" = "standard" ] || [ "$mode" = "full" ]; then
    TEST_COUNT=$(find "$FIXTURE_PATH" -type f \( -path "*__tests__*" -o -name "*.test.*" -o -name "*.spec.*" -o -name "test_*.py" -o -path "*/tests/*.py" \) | wc -l | tr -d ' ')
    if [ "$TEST_COUNT" -gt 0 ]; then
      inc_pass "Has $TEST_COUNT test file(s)"
    else
      inc_warn "No test files found (may be intentional for this eval)"
    fi
  fi

  # Check for package.json (if not a no-tooling fixture)
  if [ -f "$FIXTURE_PATH/package.json" ]; then
    inc_pass "Has package.json"
  elif echo "$name" | grep -q "no-tooling"; then
    inc_pass "No package.json (expected for no-tooling fixture)"
  else
    inc_warn "No package.json found"
  fi
done

# --- Cross-check: sequential IDs ---
printf "\n=== Cross-checks ===\n"
if command -v python3 >/dev/null 2>&1; then
  python3 -c "
import json, sys
data = json.load(open('$EVALS_JSON'))
evals = data.get('evals', [])
ids = [e['id'] for e in evals]
expected = list(range(1, len(ids) + 1))
ok = True
if ids == expected:
    print('  ✓ IDs are sequential (1-%d)' % len(ids))
else:
    print('  ✗ IDs are NOT sequential: got %s, expected %s' % (ids, expected))
    ok = False

names = [e['name'] for e in evals]
dupes = set(n for n in names if names.count(n) > 1)
if dupes:
    print('  ✗ Duplicate eval names: %s' % ', '.join(dupes))
    ok = False
else:
    print('  ✓ All eval names are unique')

if not ok:
    sys.exit(1)
"
fi

# --- Report ---
read PASS FAIL WARN < "$COUNTER_FILE" || true
printf "\n=== Summary ===\n"
printf "Passed: %d | Failed: %d | Warnings: %d\n" "$PASS" "$FAIL" "$WARN"

if [ "$FAIL" -gt 0 ]; then
  printf "\n⚠ %d failure(s) found. Review above.\n" "$FAIL"
  exit 1
else
  printf "\nAll checks passed.\n"
  exit 0
fi
