#!/bin/zsh
# Head to head against the live bot (mD16 = one14): arms given as arguments; local ladder maps first, then the generated
# maps (64x16 and 24x12 before 24x64), both seats, seed 1. P games at a time (default 6). Skips games that have a result.
cd ~/meow-redteam || exit 1
P=${H2H_P:-10}
MAPS=()
for m in maps/ladder/ladder_*.map; do MAPS+=($m); done
for sz in 64x16 24x12 24x64; do
  for m in $(ls solo/runs/h2h_mNps_v13 | sed 's/-seed.*//' | sort -u | grep "_${sz}_"); do MAPS+=(maps/gx/$m.map); done
done
n=0
for m in $MAPS; do
  N=$(basename $m .map)
  for a in "$@"; do
    for s in 0 1; do
      O=solo/runs/h2h_${a}_v16/$N-seed1-side$s
      [ -e $O/result.txt ] && continue
      if [ $s = 0 ]; then ./play.sh solo/bots/$a solo/bots/mD16 $m 1 $O > /dev/null 2>&1 &
      else ./play.sh solo/bots/mD16 solo/bots/$a $m 1 $O > /dev/null 2>&1 &; fi
      n=$((n+1))
      [ $((n % P)) -eq 0 ] && wait
    done
  done
done
wait
echo "h2h17-done $* $(date '+%T')" >> solo/runs/run.log
python3 solo/tools/h2h_tally.py | grep "_v16"
