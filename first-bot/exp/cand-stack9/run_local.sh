#!/bin/bash
# stack9 local check (at most 3 games at a time): the all-off fingerprint (1 game at a time) beside the a-layout eval (2 at a time),
# then the b-layout eval (3 at a time). Opponents proxy4_king, proxy4_swarm, proxy4_elim.
cd "$(dirname "$0")/../.."
node tools/fingerprint.js --same exp/cand-stack8/bot exp/cand-stack9/bot-off --maps portals,slithery_fight > exp/cand-stack9/fingerprint-off.log 2>&1 &
FP=$!
node tools/eval.js --bot exp/cand-stack9/bot --label stack9-a-px4 --opps proxy4_king,proxy4_swarm,proxy4_elim --seeds 1 --maps maps/online-20260927 --jobs 2 > exp/cand-stack9/eval-a.log 2>&1
wait $FP
node tools/eval.js --bot exp/cand-stack9/bot --label stack9-b-px4 --opps proxy4_king,proxy4_swarm,proxy4_elim --seeds 2 --maps maps/server-b --jobs 3 > exp/cand-stack9/eval-b.log 2>&1
echo done > exp/cand-stack9/LOCAL-DONE
