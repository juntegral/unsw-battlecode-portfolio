#!/bin/zsh
# lcheck2.zsh <arm> : build nothing; after lcheck.zsh has finished, play <arm> against m3base on the local ladder maps
# (both seats, seed 1, 4 at a time) and print it beside the live bot's games (lc_mNps).
T=~/.claude/jobs/e2109d93/tmp
while pgrep -f "tmp/lcheck.zsh" > /dev/null; do sleep 15; done
cd ~/meow-redteam || exit 1
a=$1
for m in maps/ladder/ladder_*.map; do
  n=$(basename $m .map)
  [ -e solo/runs/lc_mNps/$n-seed1-side0/result.txt ] || ./play.sh solo/bots/mNps solo/bots/m3base $m 1 solo/runs/lc_mNps/$n-seed1-side0 > /dev/null 2>&1 &
  [ -e solo/runs/lc_mNps/$n-seed1-side1/result.txt ] || ./play.sh solo/bots/m3base solo/bots/mNps $m 1 solo/runs/lc_mNps/$n-seed1-side1 > /dev/null 2>&1 &
  [ -e solo/runs/lc_$a/$n-seed1-side0/result.txt ] || ./play.sh solo/bots/$a solo/bots/m3base $m 1 solo/runs/lc_$a/$n-seed1-side0 > /dev/null 2>&1 &
  [ -e solo/runs/lc_$a/$n-seed1-side1/result.txt ] || ./play.sh solo/bots/m3base solo/bots/$a $m 1 solo/runs/lc_$a/$n-seed1-side1 > /dev/null 2>&1 &
  wait
done
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
python3 -B $T/lcheck.py lc_mNps lc_$a > $T/lcheck-$a.txt 2>&1
echo "lc2-done $a $(date '+%T')" >> ~/meow-redteam/solo/runs/run.log
