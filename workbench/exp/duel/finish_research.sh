#!/bin/bash
set -euo pipefail
while ! rg -q '^TABLES READY' exp/duel/finish-tables.log; do
  if rg -q '^Error:|RESOURCE PAUSE' exp/duel/aggregate-full-final.log 2>/dev/null; then exit 1; fi
  node -e 'require("./exp/duel/setup").guard()'
  sleep 30
done
printf 'STAGE independent tables and full classes\n'
nice -n 10 python3 exp/duel/verify.py > exp/duel/verify-tables.log 2>&1 &
duel_verify_pid=$!
nice -n 10 node exp/duel/deep.js > exp/duel/deep.log 2>&1 &
duel_deep_pid=$!
wait "$duel_verify_pid"
wait "$duel_deep_pid"
printf 'STAGE render selected boards\n'
nice -n 10 python3 exp/duel/draw.py > exp/duel/draw.log 2>&1 &
duel_board_pid=$!
nice -n 10 python3 exp/duel/draw_micro.py > exp/duel/draw-micro.log 2>&1 &
duel_micro_pid=$!
wait "$duel_board_pid"
wait "$duel_micro_pid"
printf 'ARTIFACTS READY\n'
