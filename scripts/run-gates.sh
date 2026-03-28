#!/bin/sh
# run-gates.sh — Run linter, formatter, type checker, test suite.
# Auto-fixes where possible. Reports only failures. POSIX-compatible.

set -e

FAILURES=""
PASS_COUNT=0

report_fail() {
  FAILURES="$FAILURES\n[FAIL] $1: $2"
}

report_pass() {
  PASS_COUNT=$((PASS_COUNT + 1))
}

# --- Linter ---
if [ -f ".eslintrc.json" ] || [ -f ".eslintrc.js" ] || [ -f ".eslintrc.yml" ] || [ -f "eslint.config.js" ] || [ -f "eslint.config.mjs" ]; then
  if npx eslint --fix . 2>/dev/null; then
    report_pass "eslint"
  else
    report_fail "Linter (ESLint)" "Auto-fix applied but errors remain. Run: npx eslint ."
  fi
elif command -v ruff >/dev/null 2>&1 && [ -f "pyproject.toml" ]; then
  if ruff check --fix . 2>/dev/null; then
    report_pass "ruff"
  else
    report_fail "Linter (Ruff)" "Auto-fix applied but errors remain. Run: ruff check ."
  fi
elif command -v flake8 >/dev/null 2>&1 && ([ -f ".flake8" ] || [ -f "setup.cfg" ]); then
  if flake8 . 2>/dev/null; then
    report_pass "flake8"
  else
    report_fail "Linter (flake8)" "Errors found. Run: flake8 ."
  fi
elif command -v golangci-lint >/dev/null 2>&1 && [ -f "go.mod" ]; then
  if golangci-lint run --fix 2>/dev/null; then
    report_pass "golangci-lint"
  else
    report_fail "Linter (golangci-lint)" "Errors found. Run: golangci-lint run"
  fi
fi

# --- Formatter ---
if [ -f ".prettierrc" ] || [ -f ".prettierrc.json" ] || [ -f ".prettierrc.js" ] || [ -f "prettier.config.js" ]; then
  if npx prettier --write . 2>/dev/null; then
    report_pass "prettier"
  else
    report_fail "Formatter (Prettier)" "Failed. Run: npx prettier --write ."
  fi
elif command -v black >/dev/null 2>&1 && [ -f "pyproject.toml" ]; then
  if black . 2>/dev/null; then
    report_pass "black"
  else
    report_fail "Formatter (Black)" "Failed. Run: black ."
  fi
elif [ -f "go.mod" ] && command -v gofmt >/dev/null 2>&1; then
  if gofmt -w . 2>/dev/null; then
    report_pass "gofmt"
  else
    report_fail "Formatter (gofmt)" "Failed. Run: gofmt -w ."
  fi
fi

# --- Type Checker ---
if [ -f "tsconfig.json" ]; then
  if npx tsc --noEmit 2>/dev/null; then
    report_pass "tsc"
  else
    report_fail "TypeChecker (tsc)" "Type errors found. Run: npx tsc --noEmit"
  fi
elif command -v mypy >/dev/null 2>&1 && ([ -f "mypy.ini" ] || [ -f ".mypy.ini" ] || [ -f "pyproject.toml" ]); then
  if mypy . 2>/dev/null; then
    report_pass "mypy"
  else
    report_fail "TypeChecker (mypy)" "Type errors found. Run: mypy ."
  fi
elif command -v pyright >/dev/null 2>&1 && [ -f "pyrightconfig.json" ]; then
  if pyright 2>/dev/null; then
    report_pass "pyright"
  else
    report_fail "TypeChecker (pyright)" "Errors found. Run: pyright"
  fi
fi

# --- Test Suite ---
if [ -f "jest.config.js" ] || [ -f "jest.config.ts" ] || [ -f "jest.config.mjs" ]; then
  if npx jest --passWithNoTests 2>/dev/null; then
    report_pass "jest"
  else
    report_fail "Tests (Jest)" "Test failures. Run: npx jest"
  fi
elif [ -f "vitest.config.ts" ] || [ -f "vitest.config.js" ] || [ -f "vitest.config.mts" ]; then
  if npx vitest run 2>/dev/null; then
    report_pass "vitest"
  else
    report_fail "Tests (Vitest)" "Test failures. Run: npx vitest run"
  fi
elif command -v pytest >/dev/null 2>&1 && ([ -f "pytest.ini" ] || [ -f "conftest.py" ] || [ -d "tests" ] || [ -f "pyproject.toml" ]); then
  if pytest 2>/dev/null; then
    report_pass "pytest"
  else
    report_fail "Tests (pytest)" "Test failures. Run: pytest"
  fi
elif [ -f "go.mod" ]; then
  if go test ./... 2>/dev/null; then
    report_pass "go test"
  else
    report_fail "Tests (go test)" "Test failures. Run: go test ./..."
  fi
elif [ -f "Cargo.toml" ]; then
  if cargo test 2>/dev/null; then
    report_pass "cargo test"
  else
    report_fail "Tests (cargo test)" "Test failures. Run: cargo test"
  fi
elif [ -f "package.json" ] && grep -q '"test"' package.json 2>/dev/null; then
  if npm test 2>/dev/null; then
    report_pass "npm test"
  else
    report_fail "Tests (npm test)" "Test failures. Run: npm test"
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
