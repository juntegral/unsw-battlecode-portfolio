#!/bin/zsh
# idle-exit (#43) on current main, online smoke, new bot only (compared by hand with the m39 main runs; no automatic table posted):
#   1) new bot vs dev1 (15 games, DEV allowance), then the report
#   2) new bot vs test4 + WeHaveQuizzes (30 games, normal allowance; run-pair.sh waits and retries on "Insufficient"), then the report
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
BOT="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/ie43-bot"
LOG=data/online/smoke/at-ie43.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
activeid() { node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}'; }

log "launcher started (pid $$)"
LIVE=$(activeid)
log "starting ie43-dev1 (new bot only vs 545); active bot before: $LIVE"
data/online/smoke/run-pair.sh ie43-dev1 "$BOT" "#36 + #42 + #39 + idle-exit (#43)" 545
P1=$(phase ie43-dev1)
log "ie43-dev1 ended; phase: $P1"
if [ "$P1" = "rolled-back" ]; then
  python3 tools/pair_report.py ie43-dev1 > data/online/smoke/ie43-dev1-report.log 2>&1
  log "ie43-dev1 report written (exit $?)"
fi

NOW=$(activeid)
if [[ "$LIVE" == <-> && "$NOW" == <-> && "$NOW" != "$LIVE" ]]; then
  log "active bot is $NOW, not $LIVE: live bot not restored, skipping ie43-test"
  log "launcher done"
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
log "active bot at end: $(activeid)"
log "launcher done"
