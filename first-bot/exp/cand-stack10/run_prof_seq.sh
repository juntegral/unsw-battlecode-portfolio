#!/bin/zsh
# PROFILE build of the final stack10 (only PROFILE on), four games against proxy4_swarm, one at a time (the a-layout eval runs 2 at a time):
# max decide() points per turn (the stack7-stack9 CPU check).
cd "~/01. Project/개인 프로젝트/unsw-heuristic"
one() { local m=$1; local n=$(basename $m .map); mkdir -p exp/cand-stack10/prof/$n && (cd exp/cand-stack10/prof/$n && nice -n 5 "../../../../tools/unswbc" run "../../../../$m" "../../bot-prof" "../../../../bots/proxy4_swarm" --sandbox --seed 1 --no-logs --no-draw -o game.replay > run.log 2>&1); }
for m in maps/online-20260927/default.map maps/online-20260927/queen_of_spades.map maps/server-b/schooltime_b.map maps/online-20260927/slithery_fight.map; do
  [ -f exp/cand-stack10/LOCAL-A-DONE ] && break
  one $m
done
echo done > exp/cand-stack10/prof/DONE
