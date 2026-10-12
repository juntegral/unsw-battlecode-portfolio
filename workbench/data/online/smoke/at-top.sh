#!/bin/zsh
# 10-08 15:5x KST: the live bot (v62 = main + seven switches + queen keeps 3) plays the teams worth learning from,
# asked by jun: larp stock zi balls (157), Cutlery (306), aAah (454). No upload, no swap: LIVE_ONLY runs.
# Run 1: 157 + 306. Run 2: 454 + WeHaveQuizzes (87, to keep one opponent in common with the earlier runs).
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
LOG=data/online/smoke/at-top.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
activeid() { node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}'; }
free_games() { node tools/online.js tickets --json 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin)['normal'];print(60-max(d['fromServer'],d['fromLedger'],d['used']))" 2>/dev/null || echo 0; }
wait_free() { for i in $(seq 1 120); do F=$(free_games); [ "$F" -ge 32 ] && { log "free games about $F"; return 0; }; sleep 60; done; return 1; }
one() {
  LABEL=$1; OPP=$2
  if ! wait_free; then log "allowance did not free up in 120 min: not starting $LABEL"; return 1; fi
  [ "$(activeid)" = "20366" ] || { log "active bot is $(activeid), not 20366: not starting $LABEL"; return 1; }
  log "starting $LABEL (live v62 vs $OPP)"
  LIVE_ONLY=1 data/online/smoke/run-pair.sh $LABEL - "live v62" $OPP
  log "$LABEL ended; phase: $(phase $LABEL); active: $(activeid)"
  python3 tools/pair_report.py $LABEL > data/online/smoke/$LABEL-report.log 2>&1
  log "$LABEL report written (exit $?)"
}
log "launcher started (pid $$)"
one top-l1 157,306
one top-l2 454,87
log "launcher done"
