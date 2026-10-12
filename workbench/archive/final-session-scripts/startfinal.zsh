#!/bin/zsh
T=~/.claude/jobs/e2109d93/tmp
pgrep -f "tmp/final19.zsh" > /dev/null || nohup zsh $T/final19.zsh > $T/final19.out 2>&1 &
sleep 50; cat $T/final19.out; date "+%H:%M:%S"; uptime | sed 's/.*load/load/'
