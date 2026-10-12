#!/bin/zsh
# Crash and timeout check of the live build (mD17) on every generated map (49 to 65,536 cells) and every ladder map,
# seat 0 against m3base, seed 1, 6 at a time. Then list any engine.log line that mentions an error, a timeout or a crash.
cd ~/meow-redteam || exit 1
n=0
for m in maps/gx/*_7x7_*.map maps/gx/*_64x64_*.map maps/gx/*_7x256_*.map maps/gx/*_256x7_*.map; do
  N=$(basename $m .map)
  [ -e solo/runs/st_mD17/$N/result.txt ] && continue
  ./play.sh solo/bots/mD17 solo/bots/m3base $m 1 solo/runs/st_mD17/$N > /dev/null 2>&1 &
  n=$((n+1)); wait
done
wait
echo "games with a result: $(ls solo/runs/st_mD17/*/result.txt | wc -l | tr -d ' ') of $(ls maps/gx/*_7x7_*.map maps/gx/*_64x64_*.map maps/gx/*_7x256_*.map maps/gx/*_256x7_*.map | wc -l | tr -d ' ')" > ~/.claude/jobs/e2109d93/tmp/stress17.txt
grep -il "timeout\|timed out\|crash\|exception\|segfault\|illegal\|invalid" solo/runs/st_mD17/*/engine.log | sed 's/.*st_mD17\///' >> ~/.claude/jobs/e2109d93/tmp/stress17.txt
echo "stress17-done $(date '+%T')" >> solo/runs/run.log
