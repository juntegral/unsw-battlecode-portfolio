#!/bin/zsh
# Start the shed-9 pairs detached; show the head-to-head tallies against one16 so far.
T=~/.claude/jobs/e2109d93/tmp
pgrep -f "tmp/shed9.zsh" > /dev/null || nohup zsh $T/shed9.zsh > $T/shed9.out 2>&1 &
sleep 2; pgrep -fl "tmp/shed9" | cut -c1-80
python3 ~/meow-redteam/solo/tools/h2h_tally.py | grep "_v16" | cut -c1-48
date "+%H:%M:%S"; uptime | sed 's/.*load/load/'
