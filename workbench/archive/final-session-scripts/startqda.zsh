#!/bin/zsh
T=~/.claude/jobs/e2109d93/tmp
pgrep -f "tmp/qda.zsh" > /dev/null || nohup zsh $T/qda.zsh > $T/qda.out 2>&1 &
sleep 30; cat $T/qda.out; ls ~/meow-redteam/maps/un2 | tr '\n' ' ' | cut -c1-400; echo; date "+%H:%M:%S"; uptime | sed 's/.*load/load/'
