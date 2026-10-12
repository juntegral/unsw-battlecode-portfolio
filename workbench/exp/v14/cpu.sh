#!/bin/zsh
# v1.4 check (e): our points per turn (unswbc's report for our team, side A) against proxy4_swarm, seed 1, on the heavy swarm maps and the scripted
# ones; one game at a time, stops below 21 GB free. Output: exp/v14/cpu/<map>.txt
cd "$(dirname "$0")/../.."
mkdir -p exp/v14/cpu
for m in online-20260927/default online-20260927/schooltime server-b/slithery_fight_b online-20260927/devil server-b/devil_b online-20260927/trophy server-b/schooltime_b online-20260927/slithery_fight; do
  [ "$(df -g / | awk 'NR==2 {print $4}')" -ge 21 ] || { echo "disk < 21 GB: stop"; exit 1; }
  n=$(basename $m)
  (cd exp/v14/cpu && nice -n 10 ../../../tools/unswbc run ../../../maps/$m.map ../../../versions/v1.4/bot ../../../bots/proxy4_swarm --sandbox --seed 1 --no-logs --no-draw -o $n.replay > $n.log 2>&1;
   grep -i "points per turn\|error\|timed out\|no reply\|exceeded\|wins" $n.log > $n.txt; rm -f $n.replay)
  echo "$n: $(grep 'team A points' exp/v14/cpu/$n.txt)"
done
echo done > exp/v14/CPU-DONE
