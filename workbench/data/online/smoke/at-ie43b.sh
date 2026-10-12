#!/bin/zsh
# idle-exit (#43) online smoke, second part only (the first launcher read the active bot too early after its rollback and skipped this):
#   new bot vs test4 + WeHaveQuizzes (30 games, normal allowance), report to a log, nothing posted automatically
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
BOT="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/ie43-bot"
LOG=data/online/smoke/at-ie43.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
activeid() { node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}'; }

log "second launcher started (pid $$)"
NOW=$(activeid)
if [ "$NOW" != "17790" ]; then
  log "active bot is $NOW, not 17790: not starting ie43-test"
  log "second launcher done"
  exit 0
fi
log "starting ie43-test (new bot only vs 19,87); active bot before: $NOW"
data/online/smoke/run-pair.sh ie43-test "$BOT" "#36 + #42 + #39 + idle-exit (#43)" 19,87
P2=$(phase ie43-test)
log "ie43-test ended; phase: $P2"
if [ "$P2" = "rolled-back" ]; then
  python3 tools/pair_report.py ie43-test > data/online/smoke/ie43-report.log 2>&1
  log "ie43-test report written (exit $?)"
fi
sleep 20
log "active bot at end: $(activeid)"
log "second launcher done"
