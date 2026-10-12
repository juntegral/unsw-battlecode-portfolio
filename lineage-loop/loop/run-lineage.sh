#!/bin/bash
# usage: caffeinate -i loop/run-lineage.sh <lineage> [model] [fallback]
# stop: touch lineages/<lineage>/STOP (현재 웨이브와 등록된 평가가 끝나면 종료)
set -eu
cd "$(dirname "$0")/.."
NODE="$(command -v node || echo ~/.aside/runtime/bin/node)"
exec "$NODE" loop/runner.js run "$@"
