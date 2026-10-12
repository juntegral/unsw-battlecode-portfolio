#!/bin/zsh
# #23 queen-no-trap online comparison: new bot only, 15 maps vs test4, WeHaveQuizzes, dev1; then the report
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
BOT="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/qn23-bot"
LOG=data/online/smoke/at-qn23.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
activeid() { node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}'; }

log "launcher started (pid $$); active bot before: $(activeid)"
data/online/smoke/run-pair.sh qn23-test "$BOT" "#23 queen-no-trap"
P=$(phase qn23-test)
log "qn23-test ended; phase: $P"
if [ "$P" = "rolled-back" ]; then
  python3 tools/pair_report.py qn23-test --post "#23 queen-no-trap" > data/online/smoke/qn23-report.log 2>&1
  log "qn23-test report written (exit $?)"
fi
log "active bot after: $(activeid)"
log "launcher done"
