#!/bin/zsh
# Candidate for the last bot: one18 + CENTER_MAX_CELLS 100000 (the centre pull and its stall release on every map size).
# Build it and play it head to head against the live bot mD18 on the ladder maps over 1000 cells, both seats, 4 at a time.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
grep -n "constexpr.*CENTER_MAX_CELLS\|constexpr.*CENTER_SMALL_CELLS" src/solo/main.cpp
MKSRC=src/solo/main.cpp python3 tools/mkbots.py "mCx=$(cat $T/one18.switches),CENTER_MAX_CELLS:100000" 2>&1 | tail -n 1
shasum bots/mCx/bot bots/mD18/bot | cut -c1-12,41-
cd ~/meow-redteam || exit 1
n=0
for N in ladder_australia_1 ladder_around_unsw_1 ladder_islands_1 ladder_slithery_fight_1 ladder_maze_1 ladder_schooltime_2; do
  m=maps/ladder/$N.map
  head -n 1 $m | cut -c1-40
  for s in 0 1; do
    O=solo/runs/h2h_mCx_v18/$N-seed1-side$s
    [ -e $O/result.txt ] && continue
    if [ $s = 0 ]; then ./play.sh solo/bots/mCx solo/bots/mD18 $m 1 $O > /dev/null 2>&1 &
    else ./play.sh solo/bots/mD18 solo/bots/mCx $m 1 $O > /dev/null 2>&1 &; fi
    n=$((n+1)); [ $((n % 4)) -eq 0 ] && wait
  done
done
wait
echo "cmax-done $(date '+%T')" >> solo/runs/run.log
