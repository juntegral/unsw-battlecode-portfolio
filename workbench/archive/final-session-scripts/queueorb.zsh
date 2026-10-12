#!/bin/zsh
# Queue the orbit arm's ladder-map check (detached) and show progress of the local batches.
T=~/.claude/jobs/e2109d93/tmp
pgrep -f "tmp/lcheck2.zsh mOrb4" > /dev/null || nohup zsh $T/lcheck2.zsh mOrb4 > /dev/null 2>&1 &
sleep 1
pgrep -fl "tmp/lcheck|tmp/h2h15" | grep -v "zsh -c" | cut -c1-90
echo "lc one11+one14: $(find ~/meow-redteam/solo/runs/lc_mNps ~/meow-redteam/solo/runs/lc_mDone11 -name result.txt | wc -l | tr -d ' ')/36"
echo "h2h hid8+qsn4: $(find ~/meow-redteam/solo/runs/h2h_mHid8_v14 ~/meow-redteam/solo/runs/h2h_mQsn4_v14 -name result.txt 2>/dev/null | wc -l | tr -d ' ')/132"
date "+%H:%M:%S"; uptime | sed 's/.*load/load/'
