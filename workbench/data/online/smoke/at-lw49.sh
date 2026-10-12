#!/bin/zsh
# 10-07 17:1x KST: online pair test of card 49 (LEADER_WAIT on). The two runs upload copies that differ by one comment line, so they are not twins on the server.
# Each run plays the live bot first, then live + #49 leader-wait, 15 maps each, in the same hour. Run 1 vs Big Bobs Bots (946), run 2 vs test4 (19).
# The exact live submission is restored after each run, so the parked copy stays parked.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
BOT="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/lw49a-bot"
REF="#49 leader-wait"
LOG=data/online/smoke/at-lw49.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
activeid() { node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}'; }
free_games() { node tools/online.js tickets --json 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin)['normal'];print(60-max(d['fromServer'],d['fromLedger'],d['used']))" 2>/dev/null || echo 0; }
wait_free() { for i in $(seq 1 75); do F=$(free_games); [ "$F" -ge 32 ] && { log "free games about $F"; return 0; }; sleep 60; done; return 1; }
one() {
  LABEL=$1; OPP=$2; NAME=$3; BOT=$4
  if ! wait_free; then log "allowance did not free up in 75 min: not starting $LABEL"; return 1; fi
  [ "$(activeid)" = "$LIVE" ] || { log "active bot is $(activeid), not $LIVE: not starting $LABEL"; return 1; }
  log "starting $LABEL (live bot, then live + #49 leader-wait, vs $OPP)"
  BASELINE=1 SMOKE_RESTORE_BEST=0 data/online/smoke/run-pair.sh $LABEL "$BOT" "$REF" $OPP
  P=$(phase $LABEL); log "$LABEL ended; phase: $P; active: $(activeid)"
  [ "$P" = "rolled-back" ] || return 1
  python3 tools/pair_report.py $LABEL --post "main + #49 leader-wait vs $NAME" > data/online/smoke/$LABEL-report.log 2>&1
  log "$LABEL report written (exit $?)"
  [ "$(activeid)" = "$LIVE" ]
}
LIVE=$(activeid)
log "launcher started (pid $$), live submission $LIVE"
B="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke"
one lw49-bob1 946 "Big Bobs Bots" "$B/lw49a-bot" && { sleep 60; one lw49-test1 19 "test4" "$B/lw49b-bot"; }
log "active bot at end: $(activeid)"
log "launcher done"
