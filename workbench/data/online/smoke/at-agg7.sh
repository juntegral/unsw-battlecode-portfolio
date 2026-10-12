#!/bin/zsh
# 10-08 08:5x KST: online test of jun's background switches (seven on) against current main, approved by jun at 08:4x KST.
# Three rounds. Each round plays current main (same code as v56) and main + seven switches, new bot only,
# 15 maps vs each of Big Bobs Bots (946) and WeHaveQuizzes (87), back to back so both see the same hours. Order alternates.
# The exact live submission is restored after each run, so the parked copy stays parked.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
B="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke"
LOG=data/online/smoke/at-agg7.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
activeid() { node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}'; }
free_games() { node tools/online.js tickets --json 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin)['normal'];print(60-max(d['fromServer'],d['fromLedger'],d['used']))" 2>/dev/null || echo 0; }
wait_free() { for i in $(seq 1 90); do F=$(free_games); [ "$F" -ge 32 ] && { log "free games about $F"; return 0; }; sleep 60; done; return 1; }
one() {
  LABEL=$1; BOT=$2; REF=$3
  if ! wait_free; then log "allowance did not free up in 90 min: not starting $LABEL"; return 1; fi
  LIVE=$(activeid)
  case "$LIVE" in 18570|18504) ;; *) log "active bot is $LIVE, not one of the two live copies: not starting $LABEL"; return 1;; esac
  log "starting $LABEL ($REF, vs 946,87), live $LIVE"
  SMOKE_RESTORE_BEST=0 data/online/smoke/run-pair.sh $LABEL "$BOT" "$REF" 946,87
  P=$(phase $LABEL); log "$LABEL ended; phase: $P; active: $(activeid)"
  [ "$P" = "rolled-back" ] || return 1
  python3 tools/pair_report.py $LABEL > data/online/smoke/$LABEL-report.log 2>&1
  log "$LABEL report written (exit $?)"
  [ "$(activeid)" = "$LIVE" ]
}
MAIN="current main code (a358ec8), baseline run for jun's switches"
AGG="current main + jun's seven background switches on"
log "launcher started (pid $$)"
one agg7-m1 "$B/sr51-bot" "$MAIN" && one agg7-b1 "$B/agg7-bot" "$AGG" && \
one agg7-b2 "$B/agg7-bot" "$AGG" && one agg7-m2 "$B/sr51-bot" "$MAIN" && \
one agg7-m3 "$B/sr51-bot" "$MAIN" && one agg7-b3 "$B/agg7-bot" "$AGG"
log "active bot at end: $(activeid)"
log "launcher done"
