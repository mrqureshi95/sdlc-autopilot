#!/bin/sh
# run-gates.sh — Run linter, formatter, type checker, test suite.
# Auto-fixes where possible. Reports only failures. POSIX-compatible.

set -e

FAILURES=""
PASS_COUNT=0
GATE_TIMEOUT="${GATE_TIMEOUT:-120}" # seconds per gate; override with env var

# Portable timeout wrapper — uses 'timeout' if available, else runs directly
run_with_timeout() {
  if command -v timeout >/dev/null 2>&1; then
    timeout "$GATE_TIMEOUT" "$@"
  else
    "$@"
  fi
}

report_fail() {
  FAILURES="$FAILURES\n[FAIL] $1: $2"
}

report_pass() {
  PASS_COUNT=$((PASS_COUNT + 1))
}

# --- Linter ---
if [ -f ".eslintrc.json" ] || [ -f ".eslintrc.js" ] || [ -f ".eslintrc.yml" ] || [ -f "eslint.config.js" ] || [ -f "eslint.config.mjs" ] || [ -f "eslint.config.ts" ]; then
  ESLINT_OUT=$(run_with_timeout npx eslint --fix . 2>&1) && ESLINT_RC=0 || ESLINT_RC=$?
  if [ "$ESLINT_RC" -eq 0 ]; then
    report_pass "eslint"
  else
    report_fail "Linter (ESLint)" "Auto-fix applied but errors remain:\n$ESLINT_OUT"
  fi
elif command -v ruff >/dev/null 2>&1 && { [ -f "ruff.toml" ] || [ -f "pyproject.toml" ]; }; then
  RUFF_OUT=$(ruff check --fix . 2>&1) && RUFF_RC=0 || RUFF_RC=$?
  if [ "$RUFF_RC" -eq 0 ]; then
    report_pass "ruff"
  else
    report_fail "Linter (Ruff)" "Auto-fix applied but errors remain:\n$RUFF_OUT"
  fi
elif command -v flake8 >/dev/null 2>&1 && ([ -f ".flake8" ] || [ -f "setup.cfg" ]); then
  FLAKE8_OUT=$(flake8 . 2>&1) && FLAKE8_RC=0 || FLAKE8_RC=$?
  if [ "$FLAKE8_RC" -eq 0 ]; then
    report_pass "flake8"
  else
    report_fail "Linter (flake8)" "Errors found:\n$FLAKE8_OUT"
  fi
elif command -v golangci-lint >/dev/null 2>&1 && [ -f "go.mod" ]; then
  GOLINT_OUT=$(golangci-lint run --fix 2>&1) && GOLINT_RC=0 || GOLINT_RC=$?
  if [ "$GOLINT_RC" -eq 0 ]; then
    report_pass "golangci-lint"
  else
    report_fail "Linter (golangci-lint)" "Errors found:\n$GOLINT_OUT"
  fi
fi

# --- Formatter ---
if [ -f ".prettierrc" ] || [ -f ".prettierrc.json" ] || [ -f ".prettierrc.js" ] || [ -f "prettier.config.js" ] || [ -f ".prettierrc.yaml" ] || [ -f ".prettierrc.toml" ]; then
  PRETTIER_OUT=$(run_with_timeout npx prettier --write . 2>&1) && PRETTIER_RC=0 || PRETTIER_RC=$?
  if [ "$PRETTIER_RC" -eq 0 ]; then
    report_pass "prettier"
  else
    report_fail "Formatter (Prettier)" "Failed:\n$PRETTIER_OUT"
  fi
elif command -v black >/dev/null 2>&1 && [ -f "pyproject.toml" ]; then
  BLACK_OUT=$(black . 2>&1) && BLACK_RC=0 || BLACK_RC=$?
  if [ "$BLACK_RC" -eq 0 ]; then
    report_pass "black"
  else
    report_fail "Formatter (Black)" "Failed:\n$BLACK_OUT"
  fi
elif [ -f "go.mod" ] && command -v gofmt >/dev/null 2>&1; then
  GOFMT_OUT=$(gofmt -w . 2>&1) && GOFMT_RC=0 || GOFMT_RC=$?
  if [ "$GOFMT_RC" -eq 0 ]; then
    report_pass "gofmt"
  else
    report_fail "Formatter (gofmt)" "Failed:\n$GOFMT_OUT"
  fi
fi

# --- Type Checker ---
if [ -f "tsconfig.json" ]; then
  TSC_OUT=$(run_with_timeout npx tsc --noEmit 2>&1) && TSC_RC=0 || TSC_RC=$?
  if [ "$TSC_RC" -eq 0 ]; then
    report_pass "tsc"
  else
    report_fail "TypeChecker (tsc)" "Type errors found:\n$TSC_OUT"
  fi
elif command -v mypy >/dev/null 2>&1 && ([ -f "mypy.ini" ] || [ -f ".mypy.ini" ] || [ -f "pyproject.toml" ]); then
  MYPY_OUT=$(mypy . 2>&1) && MYPY_RC=0 || MYPY_RC=$?
  if [ "$MYPY_RC" -eq 0 ]; then
    report_pass "mypy"
  else
    report_fail "TypeChecker (mypy)" "Type errors found:\n$MYPY_OUT"
  fi
elif command -v pyright >/dev/null 2>&1 && [ -f "pyrightconfig.json" ]; then
  PYRIGHT_OUT=$(pyright 2>&1) && PYRIGHT_RC=0 || PYRIGHT_RC=$?
  if [ "$PYRIGHT_RC" -eq 0 ]; then
    report_pass "pyright"
  else
    report_fail "TypeChecker (pyright)" "Errors found:\n$PYRIGHT_OUT"
  fi
fi

# --- Test Suite ---
if [ -f "jest.config.js" ] || [ -f "jest.config.ts" ] || [ -f "jest.config.mjs" ]; then
  JEST_OUT=$(run_with_timeout npx jest --passWithNoTests 2>&1) && JEST_RC=0 || JEST_RC=$?
  if [ "$JEST_RC" -eq 0 ]; then
    report_pass "jest"
  else
    report_fail "Tests (Jest)" "Test failures:\n$JEST_OUT"
  fi
elif [ -f "vitest.config.ts" ] || [ -f "vitest.config.js" ] || [ -f "vitest.config.mts" ]; then
  VITEST_OUT=$(run_with_timeout npx vitest run 2>&1) && VITEST_RC=0 || VITEST_RC=$?
  if [ "$VITEST_RC" -eq 0 ]; then
    report_pass "vitest"
  else
    report_fail "Tests (Vitest)" "Test failures:\n$VITEST_OUT"
  fi
elif command -v pytest >/dev/null 2>&1 && ([ -f "pytest.ini" ] || [ -f "conftest.py" ] || [ -d "tests" ] || [ -f "pyproject.toml" ]); then
  PYTEST_OUT=$(pytest 2>&1) && PYTEST_RC=0 || PYTEST_RC=$?
  if [ "$PYTEST_RC" -eq 0 ]; then
    report_pass "pytest"
  else
    report_fail "Tests (pytest)" "Test failures:\n$PYTEST_OUT"
  fi
elif [ -f "go.mod" ]; then
  GOTEST_OUT=$(go test ./... 2>&1) && GOTEST_RC=0 || GOTEST_RC=$?
  if [ "$GOTEST_RC" -eq 0 ]; then
    report_pass "go test"
  else
    report_fail "Tests (go test)" "Test failures:\n$GOTEST_OUT"
  fi
elif [ -f "Cargo.toml" ]; then
  CARGO_OUT=$(cargo test 2>&1) && CARGO_RC=0 || CARGO_RC=$?
  if [ "$CARGO_RC" -eq 0 ]; then
    report_pass "cargo test"
  else
    report_fail "Tests (cargo test)" "Test failures:\n$CARGO_OUT"
  fi
elif [ -f "package.json" ] && grep -q '"test"' package.json 2>/dev/null; then
  NPM_OUT=$(run_with_timeout npm test 2>&1) && NPM_RC=0 || NPM_RC=$?
  if [ "$NPM_RC" -eq 0 ]; then
    report_pass "npm test"
  else
    report_fail "Tests (npm test)" "Test failures:\n$NPM_OUT"
  fi
fi

# --- Report ---
if [ -n "$FAILURES" ]; then
  printf '\n=== Gate Failures ===\n'
  printf '%b\n' "$FAILURES"
  exit 1
else
  printf "All %d gates passed.\n" "$PASS_COUNT"
  exit 0
fi
