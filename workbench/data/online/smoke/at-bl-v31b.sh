#!/bin/zsh
# Re-run of the live bot v31 against test4 + WeHaveQuizzes (no upload, no swap). Retries until the hourly allowance allows 30 games.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
LOG=data/online/smoke/at-bl-v31.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
log "re-run queued (pid $$)"
for i in {1..40}; do
  while pgrep -f "at-q[a-z0-9]+[.]sh|unsw-swarm/data/online/smoke/run-pair[.]sh" > /dev/null; do sleep 20; done
  node tools/submit.js active 2>&1 | tail -1 | grep -q "^17790 " || { log "active bot is not 17790; stopping"; exit 1; }
  log "starting bl-v31-test, try $i"
  LIVE_ONLY=1 data/online/smoke/run-pair.sh bl-v31-test - "more live bot games" 19,87
  [ -s data/online/smoke/bl-v31-test-result.txt ] && { log "bl-v31-test finished"; break; }
  log "bl-v31-test did not start; waiting 2 min"
  sleep 120
done
log "re-run done"
