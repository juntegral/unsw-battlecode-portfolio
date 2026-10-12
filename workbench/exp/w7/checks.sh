#!/bin/zsh
# v1.7 / W7 checks: CPU (our points per turn: side A against proxy4_swarm, seed 1) for the W7 builds on small boards, and the upload smoke
# replica of versions/v1.7/bot. One game at a time; an existing result file is skipped (resumable).
cd "$(dirname "$0")/../.."
X=exp/w7
diskok() { [ "$(df -g / | awk 'NR==2 {print $4}')" -ge 21 ]; }
mkdir -p $X/cpu
for b in bot-ab bot-a2; do
  for m in online-20260927/trophy bundled/default_small bundled/Colosseum generated/gen_S_03 online-20260927/devil; do
    n=$b-$(basename $m); [ -f $X/cpu/$n.txt ] && continue; diskok || { echo "disk < 21 GB: stop"; exit 1; }
    until [ "$(pgrep -f 'unswbc-clean.py run' | wc -l)" -lt 6 ]; do sleep 10; done
    (cd $X/cpu && nice -n 10 ../../../tools/unswbc run ../../../maps/$m.map ../$b ../../../bots/proxy4_swarm --sandbox --seed 1 --no-logs --no-draw -o $n.replay > $n.log 2>&1;
     grep -i "points per turn\|error\|timed out\|no reply\|exceeded\|wins" $n.log > $n.txt; rm -f $n.replay)
  done
done
if [ ! -f $X/smoke-upload.DONE ]; then
  nice -n 10 node exp/v1/smoke_upload.js versions/v1.7/bot > $X/smoke-upload.txt 2>&1; echo "exit $?" >> $X/smoke-upload.txt; echo done > $X/smoke-upload.DONE
fi
echo "checks done"
