#!/bin/bash
set -euo pipefail
while ! rg -q '^TACTICAL DONE' exp/duel/tactical-resume.log; do
  if rg -q '^Error:|RESOURCE PAUSE' exp/duel/tactical-resume.log; then exit 1; fi
  node -e 'require("./exp/duel/setup").guard()'
  sleep 30
done
printf 'STAGE tactical and strict tables\n'
nice -n 10 node exp/duel/aggregate_tactical.js > exp/duel/aggregate-tactical.log 2>&1 &
duel_tc_pid=$!
nice -n 10 node exp/duel/aggregate.js strict > exp/duel/aggregate-strict-final.log 2>&1 &
duel_strict_pid=$!
wait "$duel_tc_pid"
wait "$duel_strict_pid"
printf 'STAGE full tables\n'
nice -n 10 node exp/duel/aggregate.js full > exp/duel/aggregate-full-final.log 2>&1
printf 'TABLES READY\n'
