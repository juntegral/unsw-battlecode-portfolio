#!/bin/bash
# Full-population extraction for the endgame king study (nice, 3 workers). Games already cached are skipped.
cd "$(dirname "$0")/../.."
SETS="cand-stack1-online cand-stack2-online cand-stack3-online cand-stack4-online cand-stack5-online cand-stack6-online cand-stack6-online-r2 cand-stack7-online cand-merge2-online cand-merge2-online-r2 cand-merge2-online-r3 cand-swarm8-online cand-avoid6-online cand-portal1-online base-px8-online base-px9d-online px-king-v2-online baseline-r1 baseline-r1b baseline-r1c"
[ -d data/online/cand-stack8-online ] && SETS="$SETS cand-stack8-online"
nice -n 10 node exp/endgame-king/extract.js online $SETS --jobs 3
nice -n 10 node exp/endgame-king/extract.js top --jobs 3 ${KEYS:+--keys $KEYS}
