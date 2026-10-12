#!/bin/zsh
# Local mechanism check: one13 (mDone13) and one14 (mNps) against m3base on the two ladder portal maps we have, both sides, seeds 1 and 2.
cd ~/meow-redteam || exit 1
for n in ladder_portals_1 ladder_australia_1; do
  m=$(ls maps/*/$n.map | head -1)
  for s in 1 2; do
    for a in mDone13 mNps; do
      ./play.sh solo/bots/$a solo/bots/m3base $m $s solo/runs/pc_$a/$n-seed$s-side0 > /dev/null 2>&1 &
      ./play.sh solo/bots/m3base solo/bots/$a $m $s solo/runs/pc_$a/$n-seed$s-side1 > /dev/null 2>&1 &
    done
  done
  wait
done
date "+%H:%M:%S"
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
python3 -B ~/.claude/jobs/e2109d93/tmp/pcheck.py
