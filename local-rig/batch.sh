#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$ROOT/.tmp"
exec "$ROOT/engine/venv/bin/python3" -B "$ROOT/tools/batch.py" "$@"
