#!/bin/zsh
# 10-08 16:5x KST: Zhe asked (16:43 KST) for v62 with the pull to centre off, tested against WeHaveQuizzes (87).
# Run 1: live v62 first, then v62 with CENTER_PULL 0, 15 maps each vs 87, same hour (BASELINE=1).
# Run 2: live v62 vs aAah (454), 15 maps, no upload (the rest of jun's top-team runs).
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
B="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke"
LOG=data/online/smoke/at-nc62.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
activeid() { node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}'; }
free_games() { node tools/online.js tickets --json 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin)['normal'];print(60-max(d['fromServer'],d['fromLedger'],d['used']))" 2>/dev/null || echo 0; }
wait_free() { for i in $(seq 1 120); do F=$(free_games); [ "$F" -ge $1 ] && { log "free games about $F"; return 0; }; sleep 60; done; return 1; }
log "launcher started (pid $$)"
if wait_free 32 && [ "$(activeid)" = "20366" ]; then
  log "starting nc62-whq1 (live v62, then v62 with the centre pull off, vs 87)"
  BASELINE=1 SMOKE_RESTORE_BEST=0 data/online/smoke/run-pair.sh nc62-whq1 "$B/nc62-bot" "pull to centre off (CENTER_PULL 0), asked by Zhe" 87
  log "nc62-whq1 ended; phase: $(phase nc62-whq1); active: $(activeid)"
  python3 tools/pair_report.py nc62-whq1 > data/online/smoke/nc62-whq1-report.log 2>&1
  log "nc62-whq1 report written (exit $?)"
else log "not starting nc62-whq1 (allowance or active bot $(activeid))"; fi
if wait_free 17 && [ "$(activeid)" = "20366" ]; then
  log "starting top-l2 (live v62 vs 454)"
  LIVE_ONLY=1 data/online/smoke/run-pair.sh top-l2 - "live v62" 454
  log "top-l2 ended; phase: $(phase top-l2); active: $(activeid)"
  python3 tools/pair_report.py top-l2 > data/online/smoke/top-l2-report.log 2>&1
  log "top-l2 report written (exit $?)"
else log "not starting top-l2 (allowance or active bot $(activeid))"; fi
log "launcher done"
