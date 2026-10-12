#!/bin/zsh
# Last-bot combos from the integration source w-one19:
#   mA19 = one18 - QUEEN_DEAD_ALL + CENTER_MAX_CELLS 100000 + QUEEN_NO_RAM
#   mB19 = mA19 + SPLIT_KNOWN_TAIL
# Sanity battery: each against m3base, seat 0, on the nine ladder maps that have a one18 baseline (nr_mD18), plus three of
# today's RED maps (baselines in qda_mD18 for two of them). 4 at a time. Tables at the end.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
A="$(sed 's/,QUEEN_DEAD_ALL:true//' $T/one18.switches),CENTER_MAX_CELLS:100000,QUEEN_NO_RAM:true"
echo "$A" > $T/one19A.switches
echo "$A,SPLIT_KNOWN_TAIL:true" > $T/one19B.switches
MKSRC=src/w-one19/main.cpp python3 tools/mkbots.py "mA19=$(cat $T/one19A.switches)" 2>&1 | tail -n 1
MKSRC=src/w-one19/main.cpp python3 tools/mkbots.py "mB19=$(cat $T/one19B.switches)" 2>&1 | tail -n 1
shasum bots/mA19/bot bots/mB19/bot | cut -c1-12,41-
cd ~/meow-redteam || exit 1
n=0
for m in maps/ladder/ladder_default_1.map maps/ladder/ladder_devil_1.map maps/ladder/ladder_weakhold_1.map maps/ladder/ladder_stripes_1.map maps/ladder/ladder_portals_1.map maps/ladder/ladder_queen_of_spades_1.map maps/ladder/ladder_trophy_1.map maps/ladder/ladder_tower_defense_1.map maps/ladder/ladder_maze_1.map maps/un2/ua_chain_448.map maps/un2/ub_tworooms.map maps/un2/ub_room8o.map; do
  N=$(basename $m .map)
  for a in mA19 mB19; do
    O=solo/runs/nr_$a/$N-seed1-side0
    [ -e $O/result.txt ] || { ./play.sh solo/bots/$a solo/bots/m3base $m 1 $O > /dev/null 2>&1 &; n=$((n+1)); }
    [ $((n % 4)) -eq 0 ] && [ $n -gt 0 ] && wait
  done
done
wait
echo "final19-done $(date '+%T')" >> solo/runs/run.log
