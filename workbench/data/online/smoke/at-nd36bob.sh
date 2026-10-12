#!/bin/zsh
# Zhe request 10-06 19:31: main with card #36 (QUEEN_DEAD_END) off, #42 and #39 on, no idle-exit; 15 games vs Big Bobs Bots (946).
# The v31 baseline is the 30 games played at 17:00 and 18:10 the same evening.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
BOT="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/nd36-bot"
REF="#42 + #39"
LABEL=nd36-bob1
LOG=data/online/smoke/at-nd36bob.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
activeid() { node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}'; }
live_is() { for i in 1 2 3 4 5 6 7 8 9 10 11 12; do [ "$(activeid)" = "$1" ] && return 0; sleep 15; done; return 1; }
free_games() { node tools/online.js tickets --json 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin)['normal'];print(60-max(d['fromServer'],d['fromLedger'],d['used']))" 2>/dev/null || echo 0; }
wait_free() { for i in $(seq 1 75); do F=$(free_games); [ "$F" -ge 17 ] && { log "free games about $F"; return 0; }; sleep 60; done; return 1; }

log "launcher started (pid $$)"
if ! wait_free; then log "allowance did not free up in 75 min: not starting"; log "launcher done"; exit 0; fi
if ! live_is 17790; then log "active bot is $(activeid), not 17790: not starting"; log "launcher done"; exit 0; fi
log "starting $LABEL (new bot only vs 946)"
data/online/smoke/run-pair.sh $LABEL "$BOT" "$REF" 946
P=$(phase $LABEL)
log "$LABEL ended; phase: $P"
if [ "$P" = "rolled-back" ]; then
  python3 tools/pair_report.py $LABEL --post "main without dead-end and idle-exit ($REF) vs Big Bobs Bots" > data/online/smoke/$LABEL-report.log 2>&1
  log "$LABEL report written (exit $?)"
fi
sleep 20
log "active bot at end: $(activeid)"
log "launcher done"
