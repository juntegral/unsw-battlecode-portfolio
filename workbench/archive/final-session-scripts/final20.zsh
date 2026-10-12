#!/bin/zsh
# one20 candidate = one19 values on w-one20 (two completions: a trapped queen under QUEEN_NO_RAM no longer marks trade or
# hunt targets; QUEEN_BLIND_STALL only between its round and five times its round). Hash checks, then the same battery
# as one19's against m3base (seat 0 on nine ladder maps; both seats on Portals, Stripes and the blind start box).
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
echo "diff against the team source: +$(diff src/solo/main.cpp src/w-one20/main.cpp | grep -c '^>') -$(diff src/solo/main.cpp src/w-one20/main.cpp | grep -c '^<')"
MKSRC=src/w-one20/main.cpp python3 tools/mkbots.py "mF20=" 2>&1 | tail -n 1
MKSRC=src/w-one20/main.cpp python3 tools/mkbots.py "mL20=$(cat $T/one18.switches)" 2>&1 | tail -n 1
MKSRC=src/w-one20/main.cpp python3 tools/mkbots.py "mD20=$(cat $T/one19.switches)" 2>&1 | tail -n 1
shasum bots/mF20/bot bots/mL20/bot bots/mD18/bot bots/mD20/bot bots/mD19/bot | cut -c1-12,41-
cd ~/meow-redteam || exit 1
n=0
for m in maps/ladder/ladder_default_1.map maps/ladder/ladder_devil_1.map maps/ladder/ladder_weakhold_1.map maps/ladder/ladder_stripes_1.map maps/ladder/ladder_portals_1.map maps/ladder/ladder_queen_of_spades_1.map maps/ladder/ladder_trophy_1.map maps/ladder/ladder_tower_defense_1.map maps/ladder/ladder_maze_1.map maps/un2/ua_chain_448.map maps/un2/ub_tworooms.map; do
  N=$(basename $m .map)
  O=solo/runs/nr_mD20/$N-seed1-side0
  [ -e $O/result.txt ] || { ./play.sh solo/bots/mD20 solo/bots/m3base $m 1 $O > /dev/null 2>&1 &; n=$((n+1)); }
  [ $((n % 4)) -eq 0 ] && [ $n -gt 0 ] && wait
done
for m in maps/un2/ua_boxnp_320.map maps/ladder/ladder_portals_1.map maps/ladder/ladder_stripes_1.map; do
  N=$(basename $m .map)
  for s in 0 1; do
    O=solo/runs/st_mD20/$N-seed1-side$s
    [ -e $O/result.txt ] && continue
    if [ $s = 0 ]; then ./play.sh solo/bots/mD20 solo/bots/m3base $m 1 $O > /dev/null 2>&1 &
    else ./play.sh solo/bots/m3base solo/bots/mD20 $m 1 $O > /dev/null 2>&1 &; fi
  done
done
wait
echo "final20-done $(date '+%T')" >> solo/runs/run.log
