#!/bin/zsh
# PROFILE build of stack9 (only PROFILE on), four games against proxy4_swarm as stack7 / stack8's CPU check: max decide() points per
# turn. Runs after the ablation runs; three games at a time, then the fourth (at most 3 local games at a time).
cd "~/01. Project/개인 프로젝트/unsw-heuristic"
while [ ! -f exp/cand-stack9/ABLATE-DONE ]; do sleep 5; done
one() { local m=$1; local n=$(basename $m .map); mkdir -p exp/cand-stack9/prof/$n && (cd exp/cand-stack9/prof/$n && nice -n 5 "../../../../tools/unswbc" run "../../../../$m" "../../bot-prof" "../../../../bots/proxy4_swarm" --sandbox --seed 1 --no-logs --no-draw -o game.replay > run.log 2>&1); }
one maps/online-20260927/default.map &
one maps/online-20260927/queen_of_spades.map &
one maps/server-b/schooltime_b.map &
wait
one maps/online-20260927/slithery_fight.map
echo done > exp/cand-stack9/prof/DONE
