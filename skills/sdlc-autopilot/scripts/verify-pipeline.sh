#!/bin/sh
# verify-pipeline.sh — External pipeline compliance verification.
# Checks FILESYSTEM EVIDENCE, not LLM self-reports.
#
# Usage: scripts/verify-pipeline.sh <mode>
#   mode: quick | standard | full
#
# Exit codes:
#   0 = all checks passed (warnings OK)
#   1 = one or more checks failed
#   2 = usage error
#
# This script is ground truth at the Ready Gate. Its output is
# deterministic and cannot be hallucinated by the LLM. When it
# contradicts the agent's self-assessment, this script wins.
#
# Checks by mode:
#   ALL:      changes exist, including untracked files, no secrets, no dangerous patterns,
#             no suppression/debug marker surprises
#   STD+FULL: test files in diff for source changes, tests pass,
#             changed Node test files run with node --test when no package runner exists,
#             coverage evidence when available, executable guardrail signal,
#             assertion-count signal in changed tests
#   FULL:     security-specific guardrail evidence
# Optional strict gate:
#   SDLC_STRICT_INVERSION=1 enables execution-based inversion verification
#   via scripts/verify-inversion.sh for supported runners
#
# POSIX-compatible. No bash-isms.

# --- Argument parsing ---
MODE="${1:-standard}"
case "$MODE" in
  quick|standard|full) ;;
  *) printf "Usage: %s <quick|standard|full>\n" "$0" >&2; exit 2 ;;
esac

# --- Counters ---
PASS=0
FAIL=0
WARN=0
SKIP=0

pass() { PASS=$((PASS + 1)); printf "[PASS] %s\n" "$1"; }
fail() { FAIL=$((FAIL + 1)); printf "[FAIL] %s\n" "$1"; [ -n "$2" ] && printf "  ↳ %s\n" "$2"; }
warn() { WARN=$((WARN + 1)); printf "[WARN] %s\n" "$1"; [ -n "$2" ] && printf "  ↳ %s\n" "$2"; }
skip() { SKIP=$((SKIP + 1)); printf "[SKIP] %s\n" "$1"; }

# --- Temp files + cleanup ---
DIFF_FILE=$(mktemp)
ADDED_FILE=$(mktemp)
EXEC_ADDED_FILE=$(mktemp)
SOURCE_FILE_LIST=$(mktemp)
UNTRACKED_FILE_LIST=$(mktemp)
trap 'rm -f "$DIFF_FILE" "$ADDED_FILE" "$EXEC_ADDED_FILE" "$SOURCE_FILE_LIST" "$UNTRACKED_FILE_LIST"' EXIT

# --- Collect diff ---
HAS_GIT=false
SOURCE_CHANGES=""
UNTRACKED_COUNT=0
if git rev-parse --git-dir >/dev/null 2>&1; then
  HAS_GIT=true

  # Uncommitted changes (staged + unstaged vs HEAD)
  git diff HEAD > "$DIFF_FILE" 2>/dev/null || true

  # If empty, try staged-only
  if [ ! -s "$DIFF_FILE" ]; then
    git diff --cached > "$DIFF_FILE" 2>/dev/null || true
  fi

  # If still empty, try branch diff against main/master
  if [ ! -s "$DIFF_FILE" ]; then
    MAIN=""
    git rev-parse --verify main >/dev/null 2>&1 && MAIN="main"
    [ -z "$MAIN" ] && git rev-parse --verify master >/dev/null 2>&1 && MAIN="master"
    CURRENT=$(git branch --show-current 2>/dev/null || true)
    if [ -n "$MAIN" ] && [ "$CURRENT" != "$MAIN" ]; then
      git diff "$MAIN"..."$CURRENT" > "$DIFF_FILE" 2>/dev/null || true
    fi
  fi

  # Include brand-new files that have not been staged or added with git add -N.
  # Ready Gate evidence must not silently ignore files the agent just created.
  git ls-files --others --exclude-standard > "$UNTRACKED_FILE_LIST" 2>/dev/null || true
  if [ -s "$UNTRACKED_FILE_LIST" ]; then
    UNTRACKED_COUNT=$(wc -l < "$UNTRACKED_FILE_LIST" | tr -d ' ')
    while IFS= read -r path; do
      [ -f "$path" ] || continue
      git diff --no-index -- /dev/null "$path" >> "$DIFF_FILE" 2>/dev/null || true
    done < "$UNTRACKED_FILE_LIST"
  fi

  # Extract added lines (exclude diff headers)
  grep '^+' "$DIFF_FILE" | grep -v '^+++' > "$ADDED_FILE" 2>/dev/null || true

  # Strip obvious comment-only additions; executable evidence is stronger than prose.
  grep -vE '^\+[[:space:]]*(//|#|/\*|\*|<!--|--[[:space:]])' "$ADDED_FILE" > "$EXEC_ADDED_FILE" 2>/dev/null || true

  SOURCE_CHANGES=$(grep '^diff --git' "$DIFF_FILE" \
    | grep -viE '(__tests__|/tests/|\.(test|spec)\.|_test\.|test_|\.md$|\.txt$|\.rst$|\.css$|\.scss$|\.sass$|\.less$|\.svg$|\.png$|\.jpg$|\.jpeg$|\.gif$|\.lock$)' || true)
  printf '%s\n' "$SOURCE_CHANGES" | awk '{print $NF}' | sed 's|^b/||' | sed '/^$/d' > "$SOURCE_FILE_LIST"
fi

# --- Header ---
printf "=== SDLC Autopilot — Pipeline Verification ===\n"
printf "Mode: %s\n\n" "$MODE"

# ─── CHECK 1: Changes exist (all modes) ───
if [ "$HAS_GIT" = false ]; then
  skip "Change detection — no git repository"
elif [ -s "$DIFF_FILE" ]; then
  COUNT=$(grep -c '^diff --git' "$DIFF_FILE" || true)
  if [ "$UNTRACKED_COUNT" -gt 0 ]; then
    pass "Changes detected: $COUNT file(s) in diff, including $UNTRACKED_COUNT untracked file(s)"
  else
    pass "Changes detected: $COUNT file(s) in diff"
  fi
else
  fail "No changes detected" "git diff is empty — was code modified?"
fi

# ─── CHECK 2: Test files in diff (standard + full) ───
if [ "$MODE" != "quick" ]; then
  if [ ! -s "$DIFF_FILE" ]; then
    skip "Test file detection — no diff available"
  else
    TEST_FILES=$(grep '^diff --git' "$DIFF_FILE" \
      | grep -iE '\.(test|spec)\.|test_|_test\.|__tests__|/tests/' || true)
    if [ -n "$TEST_FILES" ]; then
      TC=$(printf '%s\n' "$TEST_FILES" | wc -l | tr -d ' ')
      pass "Test files in diff: $TC test file(s)"
    elif [ -n "$SOURCE_CHANGES" ]; then
      fail "No test files in diff" "Changed source files without corresponding test updates"
    else
      warn "No test files in diff" "Expected new/modified test files for standard/full mode"
    fi
  fi
fi

# ─── CHECK 3: Tests pass (standard + full) ───
if [ "$MODE" != "quick" ]; then
  TEST_RC=999
  TEST_OUT=""

  if [ -f "jest.config.js" ] || [ -f "jest.config.ts" ] || [ -f "jest.config.mjs" ]; then
    TEST_OUT=$(npx jest --passWithNoTests 2>&1) && TEST_RC=0 || TEST_RC=$?
  elif [ -f "vitest.config.ts" ] || [ -f "vitest.config.js" ] || [ -f "vitest.config.mts" ]; then
    TEST_OUT=$(npx vitest run 2>&1) && TEST_RC=0 || TEST_RC=$?
  elif command -v pytest >/dev/null 2>&1 && \
       { [ -f "pytest.ini" ] || [ -f "conftest.py" ] || [ -d "tests" ] || [ -f "pyproject.toml" ]; }; then
    TEST_OUT=$(pytest 2>&1) && TEST_RC=0 || TEST_RC=$?
  elif [ -f "go.mod" ]; then
    TEST_OUT=$(go test ./... 2>&1) && TEST_RC=0 || TEST_RC=$?
  elif [ -f "Cargo.toml" ]; then
    TEST_OUT=$(cargo test 2>&1) && TEST_RC=0 || TEST_RC=$?
  elif [ -f "package.json" ] && grep -q '"test"' package.json 2>/dev/null; then
    TEST_OUT=$(npm test 2>&1) && TEST_RC=0 || TEST_RC=$?
  elif command -v node >/dev/null 2>&1 && [ -s "$DIFF_FILE" ]; then
    NODE_TEST_FILES=$(grep '^diff --git' "$DIFF_FILE" \
      | awk '{print $NF}' \
      | sed 's|^b/||' \
      | grep -iE '(__tests__/.*\.(test|spec)\.m?js$|/tests/.*\.(test|spec)\.m?js$|\.(test|spec)\.m?js$|_test\.m?js$|test_.*\.m?js$)' || true)

    if [ -n "$NODE_TEST_FILES" ]; then
      set --
      for f in $NODE_TEST_FILES; do
        [ -f "$f" ] && set -- "$@" "$f"
      done
      if [ "$#" -gt 0 ]; then
        TEST_OUT=$(node --test "$@" 2>&1) && TEST_RC=0 || TEST_RC=$?
      fi
    fi
  fi

  if [ "$TEST_RC" -eq 999 ]; then
    skip "Test execution — no test runner detected"
  elif [ "$TEST_RC" -eq 0 ]; then
    pass "Tests pass"
  else
    SUMMARY=$(printf '%s\n' "$TEST_OUT" | tail -5)
    fail "Tests failing" "$SUMMARY"
  fi
fi

# ─── CHECK 4: Coverage evidence for changed source files (standard + full) ───
if [ "$MODE" != "quick" ]; then
  if [ ! -s "$SOURCE_FILE_LIST" ]; then
    skip "Coverage evidence — no changed source files"
  else
    COVERAGE_ARTIFACT=""
    for candidate in coverage/lcov.info coverage/coverage-final.json coverage.xml; do
      if [ -f "$candidate" ]; then
        COVERAGE_ARTIFACT="$candidate"
        break
      fi
    done

    COVERAGE_CONFIG=false
    if [ -n "$COVERAGE_ARTIFACT" ]; then
      COVERAGE_CONFIG=true
    elif { [ -f package.json ] && grep -qi 'coverage' package.json 2>/dev/null; } \
      || [ -f .coveragerc ] \
      || { [ -f pyproject.toml ] && grep -qi 'pytest-cov\|coverage' pyproject.toml 2>/dev/null; } \
      || { [ -f tox.ini ] && grep -qi 'coverage' tox.ini 2>/dev/null; }; then
      COVERAGE_CONFIG=true
    fi

    if [ -n "$COVERAGE_ARTIFACT" ]; then
      COVERED=0
      while IFS= read -r src; do
        [ -z "$src" ] && continue
        [ ! -f "$src" ] && continue
        base=${src##*/}
        if grep -Fq "$src" "$COVERAGE_ARTIFACT" 2>/dev/null || grep -Fq "$base" "$COVERAGE_ARTIFACT" 2>/dev/null; then
          COVERED=$((COVERED + 1))
        fi
      done < "$SOURCE_FILE_LIST"

      if [ "$COVERED" -gt 0 ]; then
        pass "Coverage evidence for changed source files: $COVERED file(s)"
      else
        fail "Coverage artifact missing changed files" "$COVERAGE_ARTIFACT does not mention any changed source file"
      fi
    elif [ "$COVERAGE_CONFIG" = true ]; then
      warn "Coverage tooling detected but no artifact found" "Expected coverage/lcov.info, coverage-final.json, or coverage.xml after tests"
    else
      skip "Coverage evidence — no coverage artifact or tooling detected"
    fi
  fi
fi

# ─── CHECK 5: Executable guardrail signal (standard + full) ───
if [ "$MODE" != "quick" ]; then
  if [ ! -s "$ADDED_FILE" ]; then
    skip "Guardrail signal — no added lines"
  else
    EXEC_GC=$(grep -ciE \
      'assert[A-Za-z_]*\(|invariant\(|validate[A-Za-z_]*\(|sanitize[A-Za-z_]*\(|safeParse\(|schema|zod|joi|yup|throw new (Error|TypeError|RangeError)|instanceof[[:space:]]|typeof[[:space:]]|return[[:space:]]+res\.status\((400|401|403|409|422)\)|expect\(.*\)\.(toThrow|toEqual|toBe|toMatch)' \
      "$EXEC_ADDED_FILE" || true)
    COMMENT_GC=$(grep -ciE 'GUARD:|INVARIANT:|guardrail|guard against|prevent recurrence' "$ADDED_FILE" || true)
    if [ "$EXEC_GC" -gt 0 ]; then
      pass "Executable guardrail signal: $EXEC_GC pattern(s)"
    elif [ "$COMMENT_GC" -gt 0 ] && [ -n "$SOURCE_CHANGES" ]; then
      fail "Comment-only guardrail signal" "Source files changed, but only comment-based guardrails were found"
    elif [ "$COMMENT_GC" -gt 0 ]; then
      warn "Comment-only guardrail signal" "Comments mention guardrails, but no executable guard pattern was found"
    else
      warn "No executable guardrail signal found" "Verification still expects real assertions, validators, or tests"
    fi
  fi
fi

# ─── CHECK 6: No secrets (all modes) ───
if [ ! -s "$ADDED_FILE" ]; then
  skip "Secret scan — no added lines"
else
  # Match secret-like assignments, exclude env var references and placeholders
  T_D_TOKEN='TO''DO'
  F_ME_TOKEN='FIX''ME'
  X_PLACEHOLDER='xx''xx'
  SECRET_EXCLUSION_PATTERN="process\.env|os\.environ|getenv|env\[|ENV\[|config\.|\.get\(|placeholder|example|changeme|$X_PLACEHOLDER|your_|$T_D_TOKEN|$F_ME_TOKEN|test|mock|fake|dummy"
  SECRETS=$(grep -iE \
    '(password|api_key|api_secret|secret_key|private_key|access_token|auth_token)[[:space:]]*[:=]' \
    "$ADDED_FILE" \
    | grep -viE \
    "$SECRET_EXCLUSION_PATTERN" \
    || true)
  if [ -z "$SECRETS" ]; then
    pass "No hardcoded secrets detected"
  else
    SC=$(printf '%s\n' "$SECRETS" | wc -l | tr -d ' ')
    fail "Potential secrets: $SC suspicious pattern(s)" "Review added lines for hardcoded credentials"
  fi
fi

# ─── CHECK 7: No dangerous patterns (all modes) ───
if [ ! -s "$ADDED_FILE" ]; then
  skip "Dangerous pattern scan — no added lines"
else
  EVAL_CALL_PATTERN='ev''al[[:space:]]*\('
  INNER_HTML_PATTERN='\.inner''HTML[[:space:]]*='
  DANGEROUS_HTML_PATTERN='dangerouslySet''InnerHTML'
  DOCUMENT_WRITE_PATTERN='document\.wri''te[[:space:]]*\('
  DANGER_PATTERN="$EVAL_CALL_PATTERN|$INNER_HTML_PATTERN|$DANGEROUS_HTML_PATTERN|$DOCUMENT_WRITE_PATTERN"
  DANGER=$(grep -E "$DANGER_PATTERN" "$ADDED_FILE" || true)
  if [ -z "$DANGER" ]; then
    pass "No dangerous code patterns"
  else
    DC=$(printf '%s\n' "$DANGER" | wc -l | tr -d ' ')
    warn "Dangerous patterns: $DC instance(s)" "Found ev""al(), inner""HTML, or similar — verify intentional"
  fi
fi

# ─── CHECK 8: Security guardrails (full only) ───
if [ "$MODE" = "full" ]; then
  if [ ! -s "$ADDED_FILE" ]; then
    skip "Security guardrail check — no added lines"
  else
    SC=$(grep -ciE \
      'csrf|xss|injection|sanitize|escape|parameterize|prepared[[:space:]]*statement|helmet|cors|rate[[:space:]]*limit|auth[[:space:]]*(check|guard|middleware|required)|permission|rbac' \
      "$ADDED_FILE" || true)
    if [ "$SC" -gt 0 ]; then
      pass "Security guardrails: $SC security-specific pattern(s)"
    else
      warn "No security-specific patterns in diff" "Full mode expects explicit security guardrails"
    fi
  fi
fi

# ─── CHECK 9: Assertion-count signal in changed tests (standard + full) ───
if [ "$MODE" != "quick" ]; then
  if [ ! -s "$DIFF_FILE" ]; then
    skip "Assertion-count signal — no diff available"
  else
    TQ_FILES=$(grep '^diff --git' "$DIFF_FILE" \
      | grep -iE '\.(test|spec)\.|test_|_test\.|__tests__|/tests/' \
      | awk '{print $NF}' | sed 's|^b/||' || true)
    if [ -z "$TQ_FILES" ]; then
      skip "Assertion-count signal — no test files in diff"
    else
      FILE_COUNT=0
      TOTAL_ASSERTS=0
      LOW_ASSERT_FILES=0
      for f in $TQ_FILES; do
        if [ -f "$f" ]; then
          C=$(grep -Eoc 'expect\(|assert[A-Za-z_]*\(|pytest\.raises|raises\(|should\.' "$f" || true)
          FILE_COUNT=$((FILE_COUNT + 1))
          TOTAL_ASSERTS=$((TOTAL_ASSERTS + C))
          if [ "$C" -lt 2 ]; then
            LOW_ASSERT_FILES=$((LOW_ASSERT_FILES + 1))
          fi
        fi
      done

      if [ "$FILE_COUNT" -eq 0 ]; then
        skip "Assertion-count signal — changed test files not present locally"
      elif [ "$TOTAL_ASSERTS" -ge $((FILE_COUNT * 2)) ] && [ "$LOW_ASSERT_FILES" -eq 0 ]; then
        pass "Assertion-count signal: $TOTAL_ASSERTS assertions across $FILE_COUNT test file(s)"
      else
        warn "Low assertion count in changed tests" "$LOW_ASSERT_FILES of $FILE_COUNT changed test file(s) have fewer than 2 assertions"
      fi
    fi
  fi
fi

# ─── CHECK 10: Suppression / debug markers (all modes) ───
if [ ! -s "$ADDED_FILE" ]; then
  skip "Suppression/debug scan — no added lines"
else
  ESLINT_DISABLE_PATTERN='eslint-''disable'
  TS_IGNORE_PATTERN='ts-''ignore'
  TS_NOCHECK_PATTERN='ts-''nocheck'
  NO_QA_PATTERN='no''qa'
  SUPPRESS_PATTERN="$ESLINT_DISABLE_PATTERN|$TS_IGNORE_PATTERN|$TS_NOCHECK_PATTERN|$NO_QA_PATTERN|pragma:[[:space:]]*no[[:space:]]*cover"
  SUPPRESS=$(grep -iE "$SUPPRESS_PATTERN" "$ADDED_FILE" || true)
  TASK_MARKER_PATTERN='TO''DO|FIX''ME|HA''CK|X''XX'
  DEBUG_PATTERN='console\.lo''g\(|debug''ger;|pdb\.set_tra''ce\(|pri''nt\('
  TASK_MARKERS=$(grep -iE "$TASK_MARKER_PATTERN" "$ADDED_FILE" || true)
  DEBUG=$(grep -E "$DEBUG_PATTERN" "$ADDED_FILE" || true)
  if [ -z "$SUPPRESS$TASK_MARKERS$DEBUG" ]; then
    pass "No suppression or debug markers added"
  else
    if [ -n "$SUPPRESS" ]; then
      fail "Suppression markers detected" "eslint/ts/python/test suppressions were added"
    elif [ -n "$TASK_MARKERS" ] && [ -n "$DEBUG" ]; then
      warn "TO""DO and debug markers detected" "temporary markers present in added lines"
    elif [ -n "$TASK_MARKERS" ]; then
      warn "TO""DO-style markers detected" "unfinished work markers present in added lines"
    else
      warn "Debug markers detected" "debug logging or breakpoints present in added lines"
    fi
  fi
fi

# ─── CHECK 11: Strict inversion verification (opt-in, standard + full) ───
if [ "$MODE" != "quick" ]; then
  if [ "${SDLC_STRICT_INVERSION:-0}" != "1" ]; then
    skip "Strict inversion verification — disabled (set SDLC_STRICT_INVERSION=1)"
  elif [ ! -x "scripts/verify-inversion.sh" ] && [ ! -f "scripts/verify-inversion.sh" ]; then
    skip "Strict inversion verification — scripts/verify-inversion.sh not found"
  else
    INVERSION_OUT=""
    if [ -n "${SDLC_INVERSION_BASE_REF:-}" ]; then
      INVERSION_OUT=$(sh scripts/verify-inversion.sh --base-ref "$SDLC_INVERSION_BASE_REF" 2>&1) && INVERSION_RC=0 || INVERSION_RC=$?
    else
      INVERSION_OUT=$(sh scripts/verify-inversion.sh 2>&1) && INVERSION_RC=0 || INVERSION_RC=$?
    fi

    if [ "$INVERSION_RC" -eq 0 ]; then
      pass "Strict inversion verification passed"
    else
      fail "Strict inversion verification failed" "$INVERSION_OUT"
    fi
  fi
fi

# --- Summary ---
TOTAL=$((PASS + FAIL + WARN + SKIP))
printf "\n"
if [ "$FAIL" -gt 0 ]; then
  printf "Result: %d/%d passed, %d failed" "$PASS" "$TOTAL" "$FAIL"
  [ "$WARN" -gt 0 ] && printf ", %d warning(s)" "$WARN"
  [ "$SKIP" -gt 0 ] && printf ", %d skipped" "$SKIP"
  printf " ❌\n"
  exit 1
elif [ "$WARN" -gt 0 ]; then
  printf "Result: %d/%d passed, %d warning(s)" "$PASS" "$TOTAL" "$WARN"
  [ "$SKIP" -gt 0 ] && printf ", %d skipped" "$SKIP"
  printf " ⚠️\n"
  exit 0
else
  printf "Result: %d/%d passed" "$PASS" "$TOTAL"
  [ "$SKIP" -gt 0 ] && printf " (%d skipped)" "$SKIP"
  printf " ✅\n"
  exit 0
fi
