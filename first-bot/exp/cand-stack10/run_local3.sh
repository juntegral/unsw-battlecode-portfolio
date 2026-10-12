#!/bin/bash
# stack10 local check, W11 upload configuration (coordinator 22:50): LNT_ON true (kint exception for any target >= 8), UTAB_ON false.
# a layout then b layout, 3 games at a time, opponents proxy4_king, proxy4_swarm, proxy4_elim. The all-off identity against stack9 was
# checked at 22:25 (bot-off: LNT_ON and UTAB_ON false). eval.js stops starting games below 20 GiB of free disk.
cd "$(dirname "$0")/../.."
node tools/eval.js --bot exp/cand-stack10/bot --label stack10-a-px4 --opps proxy4_king,proxy4_swarm,proxy4_elim --seeds 1 --maps maps/online-20260927 --jobs 3 > exp/cand-stack10/eval-a.log 2>&1
echo done > exp/cand-stack10/LOCAL-A-DONE
node tools/eval.js --bot exp/cand-stack10/bot --label stack10-b-px4 --opps proxy4_king,proxy4_swarm,proxy4_elim --seeds 2 --maps maps/server-b --jobs 3 > exp/cand-stack10/eval-b.log 2>&1
echo done > exp/cand-stack10/LOCAL-DONE
