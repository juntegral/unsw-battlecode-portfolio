#!/bin/zsh
# After the #39 online test: 15 more games of the live bot v31 against dev1 (no upload, no swap), then,
# when the normal allowance is back, 30 more against test4 + WeHaveQuizzes. Thickens the v31 baseline.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
LOG=data/online/smoke/at-bl-v31.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
log "queued (pid $$)"
while pgrep -f "at-qs39b[.]sh|unsw-swarm/data/online/smoke/run-pair[.]sh" > /dev/null; do sleep 20; done
node tools/submit.js active 2>&1 | tail -1 | grep -q "^17790 " || { log "active bot is not 17790; stopping"; exit 1; }
log "starting bl-v31-dev1 (live only, 15 games vs dev1)"
LIVE_ONLY=1 data/online/smoke/run-pair.sh bl-v31-dev1 - "more live bot games" 545
log "bl-v31-dev1 ended"
while pgrep -f "at-q[a-z0-9]+[.]sh" > /dev/null; do sleep 30; done
node tools/submit.js active 2>&1 | tail -1 | grep -q "^17790 " || { log "active bot is not 17790; stopping before the normal run"; exit 1; }
log "starting bl-v31-test (live only, 30 games vs test4 + WeHaveQuizzes)"
LIVE_ONLY=1 data/online/smoke/run-pair.sh bl-v31-test - "more live bot games" 19,87
log "bl-v31-test ended"
log "done"
