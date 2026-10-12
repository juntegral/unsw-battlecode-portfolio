#!/bin/bash
set -euo pipefail
# Orchestration only: primary/tactical extraction uses two workers, raw verification one.
while ! rg -q '^EXTRACTED' exp/duel/extract.log; do
  if rg -q 'RESOURCE PAUSE|^Error:|^TypeError:|^RangeError:' exp/duel/extract.log; then
    printf 'PRIMARY FAILED; inspect extract.log\n'
    exit 1
  fi
  nice -n 10 node -e 'require("./exp/duel/setup").guard()'
  sleep 30
done
printf 'STAGE final inventory and incremental extraction\n'
nice -n 10 node exp/duel/late_refresh.js > exp/duel/late-refresh.log 2>&1
printf 'STAGE all direct tactical contacts\n'
nice -n 10 node exp/duel/run_tactical.js > exp/duel/tactical.log 2>&1
printf 'STAGE tactical aggregation\n'
nice -n 10 node exp/duel/aggregate_tactical.js > exp/duel/aggregate-tactical.log 2>&1
printf 'STAGE corrected strict aggregation\n'
nice -n 10 node exp/duel/aggregate.js strict > exp/duel/aggregate-strict-final.log 2>&1
printf 'STAGE corrected full aggregation\n'
nice -n 10 node exp/duel/aggregate.js full > exp/duel/aggregate-full-final.log 2>&1
printf 'PIPELINE TABLES READY\n'
