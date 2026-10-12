#!/bin/zsh
# v1.7 W15a checks: CPU (our points per turn: side A against proxy4_swarm, seed 1) for the W15a builds on maze / pocket boards and Trophy.
# One game at a time inside the machine-wide cap; an existing result file is skipped (resumable).
cd "$(dirname "$0")/../.."
X=exp/w15a
diskok() { [ "$(df -g / | awk 'NR==2 {print $4}')" -ge 21 ]; }
mkdir -p $X/cpu
for b in bot-base bot-s bot-k bot-p; do
  for m in generated/gen_M_07 generated/gen_X_07 generated/gen_S_03 bundled/autarky online-20260927/trophy; do
    n=$b-$(basename $m); [ -f $X/cpu/$n.txt ] && continue; diskok || { echo "disk < 21 GB: stop"; exit 1; }
    until [ "$(pgrep -f 'unswbc-clean.py run' | wc -l)" -lt 6 ]; do sleep 10; done
    (cd $X/cpu && nice -n 10 ../../../tools/unswbc run ../../../maps/$m.map ../$b ../../../bots/proxy4_swarm --sandbox --seed 1 --no-logs --no-draw -o $n.replay > $n.log 2>&1;
     grep -i "points per turn\|error\|timed out\|no reply\|exceeded\|wins" $n.log > $n.txt; rm -f $n.replay)
  done
done
echo "checks done"
