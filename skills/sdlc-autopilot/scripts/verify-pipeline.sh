#!/bin/sh
# Resolve bundled resources independently of the target project cwd.
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$SCRIPT_DIR/evidence.py" verify "$@"
