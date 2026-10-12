#!/bin/zsh
# Zhe's request 10-06 16:46: v31 (live) against main + idle-exit (#43), both vs Big Bobs Bots (946), two passes of 15 + 15 games.
# Each pass: BASELINE=1 plays the live bot first, then uploads and swaps to the new bot, then swaps back. The table posts after each pass.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
BOT="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/ie43-bot"
REF="#36 + #42 + #39 + idle-exit (#43)"
LOG=data/online/smoke/at-ie43bbb.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
activeid() { node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}'; }
# the server can show the test bot for a moment after a swap back: read it several times before giving up
live_is() { for i in 1 2 3 4 5 6 7 8 9 10 11 12; do [ "$(activeid)" = "$1" ] && return 0; sleep 15; done; return 1; }

log "launcher started (pid $$)"
for PASS in 1 2; do
  LABEL=ie43-bbb$PASS
  if ! live_is 17790; then
    log "active bot is $(activeid), not 17790: not starting $LABEL"
    break
  fi
  log "starting $LABEL (live bot, then new bot, vs 946)"
  BASELINE=1 data/online/smoke/run-pair.sh $LABEL "$BOT" "$REF" 946
  P=$(phase $LABEL)
  log "$LABEL ended; phase: $P"
  if [ "$P" = "rolled-back" ]; then
    python3 tools/pair_report.py $LABEL --post "$REF vs Big Bobs Bots, pass $PASS of 2" > data/online/smoke/$LABEL-report.log 2>&1
    log "$LABEL report written (exit $?)"
  else
    log "$LABEL did not finish cleanly, stopping"
    break
  fi
done
sleep 20
log "active bot at end: $(activeid)"
log "launcher done"
