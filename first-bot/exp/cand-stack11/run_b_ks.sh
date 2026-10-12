#!/bin/zsh
# stack11 local check, last step (replaces run_local.sh's two-slot b step, 23:31): once the a-layout eval (pid 91309) and the
# proxy4_elim b-layout eval (pid 704) have ended, play the b-layout games against proxy4_king and proxy4_swarm three at a time.
cd "~/01. Project/개인 프로젝트/unsw-heuristic"
X=exp/cand-stack11
while kill -0 91309 2>/dev/null || kill -0 704 2>/dev/null; do sleep 3; done
echo done > $X/LOCAL-A-DONE
node tools/eval.js --bot $X/bot --label stack11-b-px4-ks --opps proxy4_king,proxy4_swarm --seeds 2 --maps maps/server-b --jobs 3 > $X/eval-b-ks.log 2>&1
echo done > $X/LOCAL-DONE
