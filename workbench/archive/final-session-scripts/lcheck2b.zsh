#!/bin/zsh
# lcheck2b.zsh <arm>... : each arm against m3base on the local ladder maps (both seats, seed 1), P games at a time, skipping
# finished games. Does NOT play the live bot's games (lcheck2.zsh mTd0 does); tabulates against lc_mNps at the end.
# Optional MAPS_ONLY="queen_of_spades trophy" restricts the maps.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam || exit 1
P=${LC_P:-4}
n=0
for m in maps/ladder/ladder_*.map; do
  N=$(basename $m .map)
  if [ -n "$MAPS_ONLY" ]; then ok=0; for k in ${=MAPS_ONLY}; do [[ $N == ladder_${k}_* ]] && ok=1; done; [ $ok = 1 ] || continue; fi
  for a in "$@"; do
    for s in 0 1; do
      O=solo/runs/lc_$a/$N-seed1-side$s
      [ -e $O/result.txt ] && continue
      if [ $s = 0 ]; then ./play.sh solo/bots/$a solo/bots/m3base $m 1 $O > /dev/null 2>&1 &
      else ./play.sh solo/bots/m3base solo/bots/$a $m 1 $O > /dev/null 2>&1 &; fi
      n=$((n+1)); [ $((n % P)) -eq 0 ] && wait
    done
  done
done
wait
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
for a in "$@"; do python3 -B $T/lcheck.py lc_mNps lc_$a > $T/lcheck-$a.txt 2>&1; done
echo "lc2b-done $* $(date '+%T')" >> ~/meow-redteam/solo/runs/run.log
