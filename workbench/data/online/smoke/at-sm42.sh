#!/bin/zsh
# tail-on-portal ping (#42) online comparison, new bot only (live bot's games already exist):
#   1) new bot vs dev1 (15 games, DEV allowance), then the report
#   2) new bot vs test4 + WeHaveQuizzes (30 games, normal allowance; run-pair.sh waits and retries on "Insufficient"), then the report
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
BOT="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/sm42-bot"
LOG=data/online/smoke/at-sm42.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
activeid() { node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}'; }

log "launcher started (pid $$)"
while pgrep -f "at-bl-v31b[.]sh|unsw-swarm/data/online/smoke/run-pair[.]sh" > /dev/null; do sleep 20; done
log "queue clear, going on"
LIVE=$(activeid)
log "starting sm42-dev1 (new bot only vs 545); active bot before: $LIVE"
data/online/smoke/run-pair.sh sm42-dev1 "$BOT" "tail-on-portal ping (#42)" 545
P1=$(phase sm42-dev1)
log "sm42-dev1 ended; phase: $P1"
if [ "$P1" = "rolled-back" ]; then
  python3 tools/pair_report.py sm42-dev1 --post "tail-on-portal ping (#42) vs dev1" > data/online/smoke/sm42-dev1-report.log 2>&1
  log "sm42-dev1 report written (exit $?)"
fi

NOW=$(activeid)
if [[ "$LIVE" == <-> && "$NOW" == <-> && "$NOW" != "$LIVE" ]]; then
  log "active bot is $NOW, not $LIVE: live bot not restored, skipping sm42-test"
  log "launcher done"
  exit 0
fi

log "starting sm42-test (new bot only vs 19,87); active bot before: $NOW"
data/online/smoke/run-pair.sh sm42-test "$BOT" "tail-on-portal ping (#42)" 19,87
P2=$(phase sm42-test)
log "sm42-test ended; phase: $P2"
if [ "$P2" = "rolled-back" ]; then
  python3 tools/pair_report.py sm42-test --post "tail-on-portal ping (#42)" > data/online/smoke/sm42-report.log 2>&1
  log "sm42-test report written (exit $?)"
fi
log "active bot at end: $(activeid)"
log "launcher done"
