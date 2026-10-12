#!/bin/zsh
# 10-07 21:2x KST: online pair test of card 48 first build (QUEEN_NO_FEED on, commit 4fa0c49), asked by Zhe at 21:20 KST.
# Each run plays the live bot first, then live + #48 queen-sacrifice v1, 15 maps each, in the same hour. One run vs Big Bobs Bots (946).
# The exact live submission is restored after each run, so the parked copy stays parked.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
BOT="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/qn48v1-bot"
REF="#48 queen-sacrifice v1"
LOG=data/online/smoke/at-qn48.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
activeid() { node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}'; }
free_games() { node tools/online.js tickets --json 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin)['normal'];print(60-max(d['fromServer'],d['fromLedger'],d['used']))" 2>/dev/null || echo 0; }
wait_free() { for i in $(seq 1 75); do F=$(free_games); [ "$F" -ge 32 ] && { log "free games about $F"; return 0; }; sleep 60; done; return 1; }
one() {
  LABEL=$1; OPP=$2; NAME=$3; BOT=$4
  if ! wait_free; then log "allowance did not free up in 75 min: not starting $LABEL"; return 1; fi
  [ "$(activeid)" = "$LIVE" ] || { log "active bot is $(activeid), not $LIVE: not starting $LABEL"; return 1; }
  log "starting $LABEL (live bot, then live + #48 queen-sacrifice v1, vs $OPP)"
  BASELINE=1 SMOKE_RESTORE_BEST=0 data/online/smoke/run-pair.sh $LABEL "$BOT" "$REF" $OPP
  P=$(phase $LABEL); log "$LABEL ended; phase: $P; active: $(activeid)"
  [ "$P" = "rolled-back" ] || return 1
  python3 tools/pair_report.py $LABEL --post "main + #48 queen-sacrifice v1 vs $NAME" > data/online/smoke/$LABEL-report.log 2>&1
  log "$LABEL report written (exit $?)"
  [ "$(activeid)" = "$LIVE" ]
}
LIVE=$(activeid)
log "launcher started (pid $$), live submission $LIVE"
B="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke"
one qn48v1-bob1 946 "Big Bobs Bots" "$B/qn48v1-bot"
log "active bot at end: $(activeid)"
log "launcher done"
