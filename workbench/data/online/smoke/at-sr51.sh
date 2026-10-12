#!/bin/zsh
# 10-08 00:1x KST: online pair test of current main (v47 + card 48 first build) + card 51 second build (TR_STALL_RELEASE on, commit 880befa), asked by Zhe at 00:05 KST. New bot only.
# Each run plays the live bot first, then live + #48 v1 + #51 stall-release, 15 maps each, in the same hour. One run vs Big Bobs Bots (946).
# The exact live submission is restored after each run, so the parked copy stays parked.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
BOT="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/sr51-bot"
REF="#48 v1 + #51 stall-release"
LOG=data/online/smoke/at-sr51.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
activeid() { node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}'; }
free_games() { node tools/online.js tickets --json 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin)['normal'];print(60-max(d['fromServer'],d['fromLedger'],d['used']))" 2>/dev/null || echo 0; }
wait_free() { for i in $(seq 1 75); do F=$(free_games); [ "$F" -ge 32 ] && { log "free games about $F"; return 0; }; sleep 60; done; return 1; }
one() {
  LABEL=$1; OPP=$2; NAME=$3; BOT=$4
  if ! wait_free; then log "allowance did not free up in 75 min: not starting $LABEL"; return 1; fi
  [ "$(activeid)" = "$LIVE" ] || { log "active bot is $(activeid), not $LIVE: not starting $LABEL"; return 1; }
  log "starting $LABEL (live bot, then live + #48 v1 + #51 stall-release, vs $OPP)"
  SMOKE_RESTORE_BEST=0 data/online/smoke/run-pair.sh $LABEL "$BOT" "$REF" $OPP
  P=$(phase $LABEL); log "$LABEL ended; phase: $P; active: $(activeid)"
  [ "$P" = "rolled-back" ] || return 1
  python3 tools/pair_report.py $LABEL --post "current main (v47 + #48 v1) + #51 stall-release vs $NAME" > data/online/smoke/$LABEL-report.log 2>&1
  log "$LABEL report written (exit $?)"
  [ "$(activeid)" = "$LIVE" ]
}
LIVE=$(activeid)
log "launcher started (pid $$), live submission $LIVE"
B="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke"
one sr51-bob1 946 "Big Bobs Bots" "$B/sr51-bot"
log "active bot at end: $(activeid)"
log "launcher done"
