#!/bin/zsh
# W2 checks C6 (versions/v1.6.1/VERSION.md §4): CPU (our points per turn: side A against proxy4_swarm, seed 1, the biggest maps and stronghold) and
# the upload smoke replica. One game at a time; a step with a DONE marker or an existing result file is skipped (resumable).
cd "$(dirname "$0")/../.."
X=exp/w2
diskok() { [ "$(df -g / | awk 'NR==2 {print $4}')" -ge 21 ]; }
mkdir -p $X/cpu
for m in online-20260927/default online-20260927/schooltime online-20260927/slithery_fight variants/slithery_fight_b online-20260927/trauma online-20260927/devil bundled/stronghold bundled/big_empty; do
  n=$(basename $m); [ -f $X/cpu/$n.txt ] && continue; diskok || { echo "disk < 21 GB: stop"; exit 1; }
  until [ "$(pgrep -f 'unswbc-clean.py run' | wc -l)" -lt 6 ]; do sleep 10; done
  (cd $X/cpu && nice -n 10 ../../../tools/unswbc run ../../../maps/$m.map ../../../versions/v1.6.1/bot ../../../bots/proxy4_swarm --sandbox --seed 1 --no-logs --no-draw -o $n.replay > $n.log 2>&1;
   grep -i "points per turn\|error\|timed out\|no reply\|exceeded\|wins" $n.log > $n.txt; rm -f $n.replay)
done
if [ ! -f $X/smoke-upload.DONE ]; then
  nice -n 10 node exp/v1/smoke_upload.js versions/v1.6.1/bot > $X/smoke-upload.txt 2>&1; echo "exit $?" >> $X/smoke-upload.txt; echo done > $X/smoke-upload.DONE
fi
echo "checks done"
