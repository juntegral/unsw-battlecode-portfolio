#!/bin/zsh
# #30 big-map-trades online comparison, from 2026-10-05 03:07 local:
#   1) new bot only vs test4 + WeHaveQuizzes (30 games, normal allowance), then the report
#   2) live bot + new bot vs dev1 (15 + 15 games, DEV allowance), then the report
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
BOT="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/tc30-bot"
LOG=data/online/smoke/at-tc30.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
activeid() { node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}'; }

log "launcher started (pid $$); waiting for 2026-10-05 03:07"
until [ "$(date +%Y%m%d%H%M)" -ge 202610050307 ]; do sleep 20; done

LIVE=$(activeid)
log "starting tc30-test (new bot only vs 19,87); active bot before: $LIVE"
data/online/smoke/run-pair.sh tc30-test "$BOT" "#30 big-map-trades" 19,87
P1=$(phase tc30-test)
log "tc30-test ended; phase: $P1"
if [ "$P1" = "rolled-back" ]; then
  python3 tools/pair_report.py tc30-test --post "#30 big-map-trades" > data/online/smoke/tc30-report.log 2>&1
  log "tc30-test report written (exit $?)"
fi

# safety: the dev1 run takes whatever is active as "the live bot", so skip it if the first run left another bot active
NOW=$(activeid)
if [[ "$LIVE" == <-> && "$NOW" == <-> && "$NOW" != "$LIVE" ]]; then
  log "active bot is $NOW, not $LIVE: live bot not restored, skipping tc30-dev1"
  log "launcher done"
  exit 0
fi

log "starting tc30-dev1 (live bot, then new bot vs 545); active bot before: $NOW"
BASELINE=1 data/online/smoke/run-pair.sh tc30-dev1 "$BOT" "#30 big-map-trades vs dev1" 545
P2=$(phase tc30-dev1)
log "tc30-dev1 ended; phase: $P2"
if [ "$P2" = "rolled-back" ]; then
  python3 tools/pair_report.py tc30-dev1 --post "#30 big-map-trades vs dev1" > data/online/smoke/tc30-dev1-report.log 2>&1
  log "tc30-dev1 report written (exit $?)"
fi
log "launcher done"
