#!/bin/bash
# stack10 local check, b layout (W11 configuration: lnt on, kint for any target >= 8, utab off), started 23:16 after the a-layout report.
cd "$(dirname "$0")/../.."
node tools/eval.js --bot exp/cand-stack10/bot --label stack10-b-px4 --opps proxy4_king,proxy4_swarm,proxy4_elim --seeds 2 --maps maps/server-b --jobs 3 > exp/cand-stack10/eval-b.log 2>&1
echo done > exp/cand-stack10/LOCAL-DONE
