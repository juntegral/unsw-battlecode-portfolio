#!/bin/zsh
# mNR = one18 + QUEEN_NO_RAM true. Pairs against the live bot's own games: mNR and mD18 each against m3base on nine ladder
# maps, seat 0, seed 1, 4 at a time; then the table.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
MKSRC=src/w-noram/main.cpp python3 tools/mkbots.py "mNR=$(cat $T/one18.switches),QUEEN_NO_RAM:true" 2>&1 | tail -n 1
MKSRC=src/w-noram/main.cpp python3 tools/mkbots.py "mNRl=$(cat $T/one18.switches)" 2>&1 | tail -n 1
shasum bots/mNR/bot bots/mNRl/bot bots/mD18/bot | cut -c1-12,41-
cd ~/meow-redteam || exit 1
n=0
for N in ladder_default_1 ladder_devil_1 ladder_weakhold_1 ladder_stripes_1 ladder_portals_1 ladder_queen_of_spades_1 ladder_trophy_1 ladder_tower_defense_1 ladder_maze_1; do
  m=maps/ladder/$N.map
  for a in mNR mD18; do
    [ -e solo/runs/nr_$a/$N-seed1-side0/result.txt ] || { ./play.sh solo/bots/$a solo/bots/m3base $m 1 solo/runs/nr_$a/$N-seed1-side0 > /dev/null 2>&1 &; n=$((n+1)); }
    [ $((n % 4)) -eq 0 ] && [ $n -gt 0 ] && wait
  done
done
wait
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
python3 -B $T/lcheck.py nr_mD18 nr_mNR > $T/lcheck-mNR.txt 2>&1
echo "noram-done $(date '+%T')" >> ~/meow-redteam/solo/runs/run.log
