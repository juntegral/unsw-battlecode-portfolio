#!/bin/zsh
# PR #37 queen-wait: rerun of the 30 games vs test4 + WeHaveQuizzes (first try stopped on a failed upload request, nothing was swapped)
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
BOT="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/qw37-bot"
LOG=data/online/smoke/at-qw37.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
log "rerun started (pid $$): qw37-test2"
data/online/smoke/run-pair.sh qw37-test2 "$BOT" "PR #37 queen-wait (#25)" 19,87
P=$(phase qw37-test2)
log "qw37-test2 ended; phase: $P"
if [ "$P" = "rolled-back" ]; then
  python3 tools/pair_report.py qw37-test2 --post "PR #37 queen-wait (#25)" > data/online/smoke/qw37-report.log 2>&1
  log "qw37-test2 report written (exit $?)"
fi
log "active bot at end: $(node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}')"
log "rerun done"
