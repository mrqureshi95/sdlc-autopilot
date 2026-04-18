#!/bin/sh
# verify-inversion.sh — Prototype execution-based inversion verifier.
#
# Goal: prove at least one changed regression test passes on the current tree
# and fails against the base revision's code.
#
# Scope:
# - Works only in git repos
# - Supports targeted Jest, Vitest, and pytest runs
# - Uses a temporary git worktree so the original workspace is untouched
# - Copies changed test-related files into the base worktree before running
#
# Limitations:
# - Prototype only: import/collection errors are treated as inconclusive,
#   because they may be caused by API drift rather than a true behavioral fail
# - Assumes test file paths do not contain newlines
# - Monorepos and custom test wrappers may require manual adaptation

set -eu

usage() {
  printf 'Usage: %s [--base-ref <git-ref>] [--keep-worktree]\n' "$0" >&2
  exit 2
}

BASE_REF=""
KEEP_WORKTREE=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --base-ref)
      [ "$#" -lt 2 ] && usage
      BASE_REF="$2"
      shift 2
      ;;
    --keep-worktree)
      KEEP_WORKTREE=1
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      usage
      ;;
  esac
done

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  printf '[FAIL] Not a git repository\n' >&2
  exit 1
fi

ROOT=$(pwd)
DIFF_FILE=$(mktemp)
TEST_FILE_LIST=$(mktemp)
TEMP_DIR=$(mktemp -d)
BASE_WORKTREE="$TEMP_DIR/base"

cleanup() {
  if [ -d "$BASE_WORKTREE" ] && [ "$KEEP_WORKTREE" -ne 1 ]; then
    git worktree remove --force "$BASE_WORKTREE" >/dev/null 2>&1 || true
  fi
  [ "$KEEP_WORKTREE" -ne 1 ] && rm -rf "$TEMP_DIR"
  rm -f "$DIFF_FILE" "$TEST_FILE_LIST"
}
trap cleanup EXIT INT TERM

collect_diff() {
  git diff HEAD > "$DIFF_FILE" 2>/dev/null || true

  if [ ! -s "$DIFF_FILE" ]; then
    git diff --cached > "$DIFF_FILE" 2>/dev/null || true
  fi

  if [ ! -s "$DIFF_FILE" ]; then
    MAIN=""
    git rev-parse --verify main >/dev/null 2>&1 && MAIN="main"
    [ -z "$MAIN" ] && git rev-parse --verify master >/dev/null 2>&1 && MAIN="master"
    CURRENT=$(git branch --show-current 2>/dev/null || true)
    if [ -n "$MAIN" ] && [ "$CURRENT" != "$MAIN" ]; then
      git diff "$MAIN"..."$CURRENT" > "$DIFF_FILE" 2>/dev/null || true
      [ -z "$BASE_REF" ] && BASE_REF=$(git merge-base "$CURRENT" "$MAIN" 2>/dev/null || true)
    fi
  fi
}

detect_runner() {
  if [ -f "jest.config.js" ] || [ -f "jest.config.ts" ] || [ -f "jest.config.mjs" ]; then
    printf 'jest'
    return 0
  fi
  if [ -f "vitest.config.ts" ] || [ -f "vitest.config.js" ] || [ -f "vitest.config.mts" ]; then
    printf 'vitest'
    return 0
  fi
  if command -v pytest >/dev/null 2>&1 && { [ -f "pytest.ini" ] || [ -f "conftest.py" ] || [ -d "tests" ] || [ -f "pyproject.toml" ]; }; then
    printf 'pytest'
    return 0
  fi
  return 1
}

run_targeted_tests() {
  run_dir=$1
  runner=$2
  shift 2

  case "$runner" in
    jest)
      (cd "$run_dir" && npx jest --runInBand --passWithNoTests -- "$@")
      ;;
    vitest)
      (cd "$run_dir" && npx vitest run "$@")
      ;;
    pytest)
      (cd "$run_dir" && pytest "$@")
      ;;
    *)
      return 2
      ;;
  esac
}

copy_test_related_files() {
  while IFS= read -r relpath; do
    [ -z "$relpath" ] && continue
    if [ -f "$ROOT/$relpath" ]; then
      mkdir -p "$BASE_WORKTREE/$(dirname "$relpath")"
      cp "$ROOT/$relpath" "$BASE_WORKTREE/$relpath"
    fi
  done < "$TEST_FILE_LIST"
}

is_inconclusive_failure() {
  output_file=$1
  grep -qiE 'Cannot find module|ModuleNotFoundError|No module named|ImportError|SyntaxError|ReferenceError|not exported|failed to collect|collection error' "$output_file"
}

collect_diff

if [ ! -s "$DIFF_FILE" ]; then
  printf '[SKIP] No diff detected\n'
  exit 0
fi

grep '^diff --git' "$DIFF_FILE" \
  | awk '{print $4}' \
  | sed 's|^b/||' \
  | grep -iE '(__tests__|/tests/|\.(test|spec)\.|_test\.|test_|setupTests|test-utils|testing)' \
  > "$TEST_FILE_LIST" || true

if [ ! -s "$TEST_FILE_LIST" ]; then
  printf '[SKIP] No changed test files detected\n'
  exit 0
fi

RUNNER=$(detect_runner || true)
if [ -z "$RUNNER" ]; then
  printf '[SKIP] No supported targeted test runner detected (Jest, Vitest, pytest)\n'
  exit 0
fi

[ -z "$BASE_REF" ] && BASE_REF="HEAD"

printf '=== Inversion Verification Prototype ===\n'
printf 'Runner: %s\n' "$RUNNER"
printf 'Base ref: %s\n' "$BASE_REF"

set --
while IFS= read -r relpath; do
  [ -n "$relpath" ] && set -- "$@" "$relpath"
done < "$TEST_FILE_LIST"

CURRENT_OUT=$(mktemp)
BASE_OUT=$(mktemp)
trap 'rm -f "$CURRENT_OUT" "$BASE_OUT"; cleanup' EXIT INT TERM

if run_targeted_tests "$ROOT" "$RUNNER" "$@" > "$CURRENT_OUT" 2>&1; then
  printf '[PASS] Current changed tests pass\n'
else
  printf '[FAIL] Current changed tests do not pass\n'
  tail -20 "$CURRENT_OUT" || true
  exit 1
fi

git worktree add --detach "$BASE_WORKTREE" "$BASE_REF" >/dev/null 2>&1

if [ -d "$ROOT/node_modules" ] && [ ! -e "$BASE_WORKTREE/node_modules" ]; then
  ln -s "$ROOT/node_modules" "$BASE_WORKTREE/node_modules"
fi
if [ -d "$ROOT/.venv" ] && [ ! -e "$BASE_WORKTREE/.venv" ]; then
  ln -s "$ROOT/.venv" "$BASE_WORKTREE/.venv"
fi

copy_test_related_files

if run_targeted_tests "$BASE_WORKTREE" "$RUNNER" "$@" > "$BASE_OUT" 2>&1; then
  printf '[FAIL] Base revision passes the changed tests\n'
  printf '  ↳ No inversion evidence: tests do not distinguish old vs new behavior\n'
  exit 1
fi

if is_inconclusive_failure "$BASE_OUT"; then
  printf '[FAIL] Base revision fails inconclusively\n'
  printf '  ↳ Likely import/collection/API drift rather than behavioral inversion\n'
  tail -20 "$BASE_OUT" || true
  exit 1
fi

printf '[PASS] Base revision fails the changed tests\n'
printf '  ↳ At least one changed test distinguishes pre-fix vs post-fix behavior\n'
exit 0