#!/bin/zsh
# #31 queen-hunt (portal rule) online comparison:
#   1) live bot, then new bot vs test4 + WeHaveQuizzes (30 + 30 games), then the report
#   2) live bot, then new bot vs dev1 (15 + 15 games, DEV allowance), then the report
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
BOT="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/qh31b-bot"
LOG=data/online/smoke/at-qh31b.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
activeid() { node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}'; }

log "launcher started (pid $$)"
LIVE=$(activeid)
log "starting qh31b-test (live then new vs 19,87); active bot before: $LIVE"
BASELINE=1 data/online/smoke/run-pair.sh qh31b-test "$BOT" "#31 queen-hunt (portal rule)" 19,87
P1=$(phase qh31b-test)
log "qh31b-test ended; phase: $P1"
if [ "$P1" = "rolled-back" ]; then
  python3 tools/pair_report.py qh31b-test --post "#31 queen-hunt (portal rule)" > data/online/smoke/qh31b-report.log 2>&1
  log "qh31b-test report written (exit $?)"
fi

NOW=$(activeid)
if [ "$NOW" != "$LIVE" ]; then
  log "active bot is $NOW, not $LIVE: stopping, skipping qh31b-dev1"
  log "launcher done"
  exit 0
fi

log "starting qh31b-dev1 (live then new vs 545); active bot before: $NOW"
BASELINE=1 data/online/smoke/run-pair.sh qh31b-dev1 "$BOT" "#31 queen-hunt (portal rule) vs dev1" 545
P2=$(phase qh31b-dev1)
log "qh31b-dev1 ended; phase: $P2"
if [ "$P2" = "rolled-back" ]; then
  python3 tools/pair_report.py qh31b-dev1 --post "#31 queen-hunt (portal rule) vs dev1" > data/online/smoke/qh31b-dev1-report.log 2>&1
  log "qh31b-dev1 report written (exit $?)"
fi
log "active bot at end: $(activeid)"
log "launcher done"
