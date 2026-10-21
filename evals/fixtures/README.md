# Evaluation fixtures

Deliberately small projects with planted bugs and security weaknesses. Never deploy
these fixtures. Their toy auth/password code is not production guidance.

Dependencies come from the exact-pinned `../runtime/package.json` and lockfile,
prepared separately into a new external directory by `prepare-eval-runtime.py`.
The harness links that runtime and copies fixtures into disposable workspaces;
fixture package manifests intentionally do not declare independently unlocked
external dependencies. Run `check-fixtures.py` rather than npm install here.
Node SQLite replaces a native build dependency. Python pagination oracles use only
the standard library; the Flask API is not executed by that oracle.

Baseline tests can pass while planted bugs remain. The monorepo intentionally has
a broken SOURCE import; its test import is valid. Semantic evaluator-owned
oracles outside the workspace catch a subset of outcomes. Human criteria, device
layout, risk decisions and agent behavior require separate assessment. Disposable
directories are not a security sandbox for hostile agent patches.
