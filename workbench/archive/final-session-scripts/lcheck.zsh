#!/bin/zsh
# Local check: one11 (mDone11) and one14 (mNps) against m3base on the nine ladder maps, both sides, seed 1, four games at a time.
cd ~/meow-redteam || exit 1
for n in ladder_stripes_1 ladder_slithery_fight_1 ladder_islands_1 ladder_tower_defense_1 ladder_schooltime_1 ladder_schooltime_2 ladder_around_unsw_1 ladder_australia_1 ladder_portals_1; do
  m=$(ls maps/*/$n.map | head -1)
  for a in mDone11 mNps; do
    [ -e solo/runs/lc_$a/$n-seed1-side0/result.txt ] || ./play.sh solo/bots/$a solo/bots/m3base $m 1 solo/runs/lc_$a/$n-seed1-side0 > /dev/null 2>&1 &
    [ -e solo/runs/lc_$a/$n-seed1-side1/result.txt ] || ./play.sh solo/bots/m3base solo/bots/$a $m 1 solo/runs/lc_$a/$n-seed1-side1 > /dev/null 2>&1 &
  done
  wait
done
date "+%H:%M:%S"
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
python3 -B ~/.claude/jobs/e2109d93/tmp/lcheck.py
echo "lc-done $(date '+%T')" >> ~/meow-redteam/solo/runs/run.log
