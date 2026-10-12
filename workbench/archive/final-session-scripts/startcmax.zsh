#!/bin/zsh
# Start the centre-pull candidate's head to head detached and show what it printed first.
T=~/.claude/jobs/e2109d93/tmp
pgrep -f "tmp/cmax.zsh" > /dev/null || nohup zsh $T/cmax.zsh > $T/cmax.out 2>&1 &
sleep 45; cat $T/cmax.out | head -n 12; date "+%H:%M:%S"; uptime | sed 's/.*load/load/'
