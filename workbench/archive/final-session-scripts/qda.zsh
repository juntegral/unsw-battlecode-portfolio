#!/bin/zsh
# mQDA = one18 without QUEEN_DEAD_ALL (the queen's dead-end terms on maps of 600 cells or fewer). Pairs against the live
# bot's own games: mQDA and mD18 each against m3base, both seats, on the small ladder maps and the new small test maps.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
SW=$(sed 's/,QUEEN_DEAD_ALL:true//' $T/one18.switches)
echo "$SW" | grep -c QUEEN_DEAD_ALL
MKSRC=src/solo/main.cpp python3 tools/mkbots.py "mQDA=$SW" 2>&1 | tail -n 1
shasum bots/mQDA/bot | cut -c1-12
cd ~/meow-redteam || exit 1
n=0
for m in maps/ladder/ladder_tower_defense_1.map maps/ladder/ladder_stripes_1.map maps/ladder/ladder_portals_1.map maps/ladder/ladder_devil_1.map maps/un2/ub_room20.map maps/un2/ub_tworooms.map maps/un2/ub_room3.map maps/un2/ua_chain_448.map maps/un2/uc_tiny7x7.map maps/un2/uc_tiny7x9.map; do
  [ -f $m ] || { echo "missing $m"; continue; }
  N=$(basename $m .map)
  for a in mQDA mD18; do
    for s in 0 1; do
      O=solo/runs/qda_$a/$N-seed1-side$s
      [ -e $O/result.txt ] && continue
      if [ $s = 0 ]; then ./play.sh solo/bots/$a solo/bots/m3base $m 1 $O > /dev/null 2>&1 &
      else ./play.sh solo/bots/m3base solo/bots/$a $m 1 $O > /dev/null 2>&1 &; fi
      n=$((n+1)); [ $((n % 4)) -eq 0 ] && wait
    done
  done
done
wait
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
python3 -B $T/lcheck.py qda_mD18 qda_mQDA > $T/lcheck-mQDA.txt 2>&1
echo "qda-done $(date '+%T')" >> ~/meow-redteam/solo/runs/run.log
