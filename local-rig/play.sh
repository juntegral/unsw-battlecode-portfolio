#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$ROOT/.tmp"
exec nice -n 15 "$ROOT/engine/venv/bin/python3" -B "$ROOT/engine/run_game.py" "$@"
