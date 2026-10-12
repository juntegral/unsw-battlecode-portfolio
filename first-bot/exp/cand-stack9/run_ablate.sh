#!/bin/bash
# stack9 ablation (local, at most 3 games at a time): after the cov-off a-layout run, lsplit without the gathering window
# (LSPLIT_END 340 instead of 430) on both layouts.
cd "$(dirname "$0")/../.."
while pgrep -f "label stack9nocov-a-px4" > /dev/null; do sleep 5; done
node tools/eval.js --bot exp/cand-stack9/bot-l340 --label stack9l340-a-px4 --opps proxy4_king,proxy4_swarm,proxy4_elim --seeds 1 --maps maps/online-20260927 --jobs 3 > exp/cand-stack9/eval-l340-a.log 2>&1
node tools/eval.js --bot exp/cand-stack9/bot-l340 --label stack9l340-b-px4 --opps proxy4_king,proxy4_swarm,proxy4_elim --seeds 2 --maps maps/server-b --jobs 3 > exp/cand-stack9/eval-l340-b.log 2>&1
echo done > exp/cand-stack9/ABLATE-DONE
