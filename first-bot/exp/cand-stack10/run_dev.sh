#!/bin/bash
# stack10 dev check on the stack8 base (exp/cand-stack10/dev8; the final build is on stack9): proxy4 opponents, a layout seed 1 then
# b layout seed 2, at most 3 games at a time. Firing, safety and the mech_check section only.
cd "$(dirname "$0")/../.."
node tools/eval.js --bot exp/cand-stack10/dev8 --label stack10dev8-a-px4 --opps proxy4_king,proxy4_swarm,proxy4_elim --seeds 1 --maps maps/online-20260927 --jobs 3 > exp/cand-stack10/dev8-eval-a.log 2>&1
node tools/eval.js --bot exp/cand-stack10/dev8 --label stack10dev8-b-px4 --opps proxy4_king,proxy4_swarm,proxy4_elim --seeds 2 --maps maps/server-b --jobs 3 > exp/cand-stack10/dev8-eval-b.log 2>&1
echo done > exp/cand-stack10/DEV8-DONE
