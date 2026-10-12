#!/bin/zsh
# PROFILE build of stack8, three games against proxy4_swarm (as cand-stack7's CPU check): max decide() points per turn
cd "~/01. Project/개인 프로젝트/unsw-heuristic"
for m in maps/online-20260927/default.map maps/online-20260927/queen_of_spades.map maps/server-b/schooltime_b.map maps/online-20260927/slithery_fight.map; do
  n=$(basename $m .map)
  mkdir -p exp/cand-stack8/prof/$n && (cd exp/cand-stack8/prof/$n && nice -n 5 "../../../../tools/unswbc" run "../../../../$m" "../../bot-prof" "../../../../bots/proxy4_swarm" --sandbox --seed 1 --no-logs --no-draw -o game.replay > run.log 2>&1)
done
echo done > exp/cand-stack8/prof/DONE
