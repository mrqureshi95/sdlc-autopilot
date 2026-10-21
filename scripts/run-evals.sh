#!/bin/sh
# Structural validation only. See check-fixtures.py and check-oracles.py for execution.
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$SCRIPT_DIR/validate-evals.py" "$@"
