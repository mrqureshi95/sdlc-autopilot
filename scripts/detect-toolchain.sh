#!/bin/sh
# detect-toolchain.sh — Detect project toolchain. Outputs JSON.
# POSIX-compatible. Graceful with missing tools.

set -e

# Helpers
cmd_exists() { command -v "$1" >/dev/null 2>&1; }
file_exists() { [ -f "$1" ]; }
dir_exists() { [ -d "$1" ]; }

# Language detection
LANGUAGE="null"
FRAMEWORK="null"
if file_exists "package.json"; then
  LANGUAGE="javascript"
  if grep -q '"next"' package.json 2>/dev/null; then FRAMEWORK="next";
  elif grep -q '"react"' package.json 2>/dev/null; then FRAMEWORK="react";
  elif grep -q '"vue"' package.json 2>/dev/null; then FRAMEWORK="vue";
  elif grep -q '"svelte"' package.json 2>/dev/null; then FRAMEWORK="svelte";
  elif grep -q '"express"' package.json 2>/dev/null; then FRAMEWORK="express";
  elif grep -q '"fastify"' package.json 2>/dev/null; then FRAMEWORK="fastify";
  fi
  if file_exists "tsconfig.json"; then LANGUAGE="typescript"; fi
elif file_exists "requirements.txt" || file_exists "pyproject.toml" || file_exists "setup.py"; then
  LANGUAGE="python"
  if file_exists "manage.py"; then FRAMEWORK="django";
  elif grep -q "flask" requirements.txt 2>/dev/null || grep -q "flask" pyproject.toml 2>/dev/null; then FRAMEWORK="flask";
  elif grep -q "fastapi" requirements.txt 2>/dev/null || grep -q "fastapi" pyproject.toml 2>/dev/null; then FRAMEWORK="fastapi";
  fi
elif file_exists "go.mod"; then
  LANGUAGE="go"
elif file_exists "Cargo.toml"; then
  LANGUAGE="rust"
elif file_exists "Gemfile"; then
  LANGUAGE="ruby"
  if file_exists "config/routes.rb"; then FRAMEWORK="rails"; fi
elif file_exists "pom.xml" || file_exists "build.gradle" || file_exists "build.gradle.kts"; then
  LANGUAGE="java"
  if grep -q "spring" pom.xml 2>/dev/null || grep -q "spring" build.gradle 2>/dev/null; then FRAMEWORK="spring"; fi
fi

# Linter
LINTER="null"
if file_exists ".eslintrc.json" || file_exists ".eslintrc.js" || file_exists ".eslintrc.yml" || file_exists "eslint.config.js" || file_exists "eslint.config.mjs"; then
  LINTER="eslint"
elif file_exists ".flake8" || { file_exists "setup.cfg" && grep -q "flake8" setup.cfg 2>/dev/null; }; then
  LINTER="flake8"
elif file_exists "pyproject.toml" && grep -q "ruff" pyproject.toml 2>/dev/null; then
  LINTER="ruff"
elif file_exists ".golangci.yml" || file_exists ".golangci.yaml"; then
  LINTER="golangci-lint"
elif file_exists ".rubocop.yml"; then
  LINTER="rubocop"
fi

# Formatter
FORMATTER="null"
if file_exists ".prettierrc" || file_exists ".prettierrc.json" || file_exists ".prettierrc.js" || file_exists "prettier.config.js"; then
  FORMATTER="prettier"
elif file_exists "pyproject.toml" && grep -q "black" pyproject.toml 2>/dev/null; then
  FORMATTER="black"
elif [ "$LANGUAGE" = "go" ]; then
  FORMATTER="gofmt"
elif [ "$LANGUAGE" = "rust" ]; then
  FORMATTER="rustfmt"
fi

# Type checker
TYPECHECKER="null"
if file_exists "tsconfig.json"; then
  TYPECHECKER="tsc"
elif file_exists "pyproject.toml" && grep -q "mypy" pyproject.toml 2>/dev/null; then
  TYPECHECKER="mypy"
elif file_exists "mypy.ini" || file_exists ".mypy.ini"; then
  TYPECHECKER="mypy"
elif file_exists "pyrightconfig.json"; then
  TYPECHECKER="pyright"
fi

# Test runner
TEST_RUNNER="null"
if file_exists "jest.config.js" || file_exists "jest.config.ts" || file_exists "jest.config.mjs"; then
  TEST_RUNNER="jest"
elif file_exists "vitest.config.ts" || file_exists "vitest.config.js" || file_exists "vitest.config.mts"; then
  TEST_RUNNER="vitest"
elif file_exists "package.json" && grep -q '"test"' package.json 2>/dev/null; then
  TEST_RUNNER="npm-test"
elif file_exists "pytest.ini" || { file_exists "pyproject.toml" && grep -q "pytest" pyproject.toml 2>/dev/null; }; then
  TEST_RUNNER="pytest"
elif file_exists "conftest.py" || dir_exists "tests"; then
  TEST_RUNNER="pytest"
elif [ "$LANGUAGE" = "go" ]; then
  TEST_RUNNER="go-test"
elif [ "$LANGUAGE" = "rust" ]; then
  TEST_RUNNER="cargo-test"
fi

# Deploy target
DEPLOY_TARGET="null"
CUSTOM_DEPLOY="null"
if file_exists "package.json" && grep -q '"deploy"' package.json 2>/dev/null; then
  CUSTOM_DEPLOY="npm-run-deploy"
elif file_exists "Makefile" && grep -q '^deploy:' Makefile 2>/dev/null; then
  CUSTOM_DEPLOY="make-deploy"
elif file_exists "deploy.sh"; then
  CUSTOM_DEPLOY="deploy.sh"
fi

if file_exists "supabase/config.toml"; then DEPLOY_TARGET="supabase";
elif file_exists "vercel.json" || dir_exists ".vercel"; then DEPLOY_TARGET="vercel";
elif file_exists "netlify.toml" || file_exists "_redirects"; then DEPLOY_TARGET="netlify";
elif file_exists "Dockerfile" || file_exists "docker-compose.yml" || file_exists "docker-compose.yaml"; then DEPLOY_TARGET="docker";
elif file_exists "serverless.yml"; then DEPLOY_TARGET="serverless";
elif file_exists "template.yaml" && grep -q "AWSTemplateFormatVersion" template.yaml 2>/dev/null; then DEPLOY_TARGET="sam";
elif dir_exists ".git" && git remote 2>/dev/null | grep -q .; then DEPLOY_TARGET="git";
fi

# Git status
GIT_STATUS="null"
GIT_BRANCH="null"
if dir_exists ".git"; then
  GIT_STATUS="initialized"
  # Sanitize branch name: whitelist only safe chars for JSON output
  GIT_BRANCH=$(git branch --show-current 2>/dev/null | sed 's/[^a-zA-Z0-9._\/-]//g' || echo "null")
  [ -z "$GIT_BRANCH" ] && GIT_BRANCH="null"
fi

# Output JSON
cat <<EOF
{
  "language": "$LANGUAGE",
  "framework": "$FRAMEWORK",
  "linter": "$LINTER",
  "formatter": "$FORMATTER",
  "type_checker": "$TYPECHECKER",
  "test_runner": "$TEST_RUNNER",
  "deploy_target": "$DEPLOY_TARGET",
  "custom_deploy": "$CUSTOM_DEPLOY",
  "git_status": "$GIT_STATUS",
  "git_branch": "$GIT_BRANCH"
}
EOF
