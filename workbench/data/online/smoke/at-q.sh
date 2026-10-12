#!/bin/zsh
# 10-08 19:0x KST: online queue runner. Reads jobs from at-q.txt, one per line, in order:
#   label|bot dir or -|description|opponent ids|mode
# mode: new (upload, swap, 15 maps per opponent, swap back) or live (live bot only, no swap).
# Opponent 545 (dev test 1) draws on the DEV allowance, the others on the normal one.
# Jobs can be appended while it runs. A line "END" stops it. One job at a time; the live bot must be LIVE_ID before each.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
Q=data/online/smoke/at-q.txt
LOG=data/online/smoke/at-q.log
LIVE_ID=${LIVE_ID:-20366}
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
activeid() { node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}'; }
free_games() { node tools/online.js tickets --json 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin)['$1'];print(60-max(d['fromServer'],d['fromLedger'],d['used']))" 2>/dev/null || echo 0; }
wait_free() { for i in $(seq 1 120); do F=$(free_games $1); [ "$F" -ge $2 ] && { log "free $1 games about $F"; return 0; }; sleep 60; done; return 1; }
log "queue runner started (pid $$), live id $LIVE_ID"
N=0
DEADLINE=$(( $(date +%s) + 18 * 3600 ))
while [ $(date +%s) -lt $DEADLINE ]; do
  LINE=$(sed -n "$((N + 1))p" $Q 2>/dev/null)
  if [ -z "$LINE" ]; then sleep 30; continue; fi
  N=$((N + 1))
  [ "$LINE" = "END" ] && break
  case "$LINE" in \#*) continue;; esac
  LABEL=${LINE%%|*}; R=${LINE#*|}; BOT=${R%%|*}; R=${R#*|}; REF=${R%%|*}; R=${R#*|}; OPP=${R%%|*}; MODE=${R#*|}
  [ -e data/online/smoke/$LABEL.json ] && { log "$LABEL already has a state file: skipped"; continue; }
  NOPP=$(echo $OPP | tr ',' '\n' | wc -l | tr -d ' ')
  NDEV=$(echo $OPP | tr ',' '\n' | grep -c '^545$')
  NNORM=$((NOPP - NDEV))
  if [ $NNORM -gt 0 ] && ! wait_free normal $((15 * NNORM + 2)); then log "normal allowance did not free up in 2 h: not starting $LABEL"; continue; fi
  if [ $NDEV -gt 0 ] && ! wait_free dev $((15 * NDEV + 2)); then log "dev allowance did not free up in 2 h: not starting $LABEL"; continue; fi
  LIVE=$(activeid)
  if [ "$LIVE" != "$LIVE_ID" ]; then log "active bot is $LIVE, not $LIVE_ID: not starting $LABEL, queue runner exits"; break; fi
  log "starting $LABEL ($MODE; $REF; vs $OPP), live $LIVE"
  if [ "$MODE" = "live" ]; then
    LIVE_ONLY=1 SMOKE_RESTORE_BEST=0 data/online/smoke/run-pair.sh $LABEL - "$REF" $OPP
  else
    SMOKE_RESTORE_BEST=0 data/online/smoke/run-pair.sh $LABEL "$BOT" "$REF" $OPP
  fi
  P=$(phase $LABEL); A=$(activeid); log "$LABEL ended; phase: $P; active: $A"
  if [ "$P" = "rolled-back" ]; then
    python3 tools/pair_report.py $LABEL > data/online/smoke/$LABEL-report.log 2>&1
    log "$LABEL report written (exit $?)"
  fi
  if [ "$A" != "$LIVE_ID" ]; then log "active bot is $A after $LABEL, not $LIVE_ID: queue runner exits"; break; fi
done
log "queue runner done"
