#!/bin/zsh
# #31 queen-hunt (third build): the dev1 half again, after the first launcher is done.
# First try stopped before anything was swapped ("our battles are live or pending").
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
BOT="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/qh31c-bot"
LOG=data/online/smoke/at-qh31c.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
while pgrep -f "at-qh31c[.]sh" > /dev/null; do sleep 20; done
log "dev1 rerun started (pid $$): qh31c-dev1b"
for try in 1 2 3 4 5 6; do
  data/online/smoke/run-pair.sh qh31c-dev1b "$BOT" "#31 queen-hunt (third build) vs dev1" 545
  P=$(phase qh31c-dev1b)
  [ "$P" != "none" ] && break
  log "qh31c-dev1b did not start (try $try), waiting 2 min"
  sleep 120
done
log "qh31c-dev1b ended; phase: $P"
if [ "$P" = "rolled-back" ]; then
  python3 tools/pair_report.py qh31c-dev1b --post "#31 queen-hunt (third build) vs dev1" > data/online/smoke/qh31c-dev1-report.log 2>&1
  log "qh31c-dev1b report written (exit $?)"
fi
log "active bot at end: $(node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}')"
log "all qh31c runs done"
