#!/bin/zsh
# Make sure the two local batches survive this session's command time limit: start each detached if it is not running.
T=~/.claude/jobs/e2109d93/tmp
pgrep -f "tmp/lcheck.zsh" > /dev/null || { nohup zsh $T/lcheck.zsh > $T/lcheck.out 2>&1 & echo "lcheck restarted"; }
pgrep -f "tmp/h2h15.zsh" > /dev/null || { nohup zsh $T/h2h15.zsh mHid8 mQsn4 > $T/h2h15.out 2>&1 & echo "h2h restarted"; }
sleep 2
pgrep -fl "tmp/lcheck.zsh|tmp/h2h15.zsh" | cut -c1-110
date "+%H:%M:%S"; uptime | sed 's/.*load/load/'
