#!/bin/zsh
T=~/.claude/jobs/e2109d93/tmp
pgrep -f "tmp/noram.zsh" > /dev/null || nohup zsh $T/noram.zsh > $T/noram.out 2>&1 &
sleep 40; cat $T/noram.out; date "+%H:%M:%S"; uptime | sed 's/.*load/load/'
