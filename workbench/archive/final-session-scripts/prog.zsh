#!/bin/zsh
# Progress and current tables of the local batches.
T=~/.claude/jobs/e2109d93/tmp
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
date "+%H:%M:%S"; uptime | sed 's/.*load/load/'
for p in "lc_mNps lc_mTd0" "lc_mTd0 lc_mHs15" "lc_mNps lc_mOrb4"; do
  echo "== $p"
  python3 -B $T/lcheck.py ${=p} 2>&1 | tail -n ${PROG_N:-1}
done
python3 ~/meow-redteam/solo/tools/h2h_tally.py | grep "_v15"
tail -n 2 data/online/smoke/at-q.log | cut -c1-110
