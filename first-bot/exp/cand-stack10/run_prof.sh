#!/bin/zsh
# PROFILE build (only PROFILE on), four games against proxy4_swarm (the stack7-stack9 CPU check): max decide() points per turn. Three games
# at a time, then the fourth (at most 3 local games at a time). usage: run_prof.sh <bot dir under exp/cand-stack10> <out dir name>
cd "~/01. Project/개인 프로젝트/unsw-heuristic"
B=$1; O=$2
one() { local m=$1; local n=$(basename $m .map); mkdir -p exp/cand-stack10/$O/$n && (cd exp/cand-stack10/$O/$n && nice -n 5 "../../../../tools/unswbc" run "../../../../$m" "../../$B" "../../../../bots/proxy4_swarm" --sandbox --seed 1 --no-logs --no-draw -o game.replay > run.log 2>&1); }
one maps/online-20260927/default.map &
one maps/online-20260927/queen_of_spades.map &
one maps/server-b/schooltime_b.map &
wait
one maps/online-20260927/slithery_fight.map
echo done > exp/cand-stack10/$O/DONE
