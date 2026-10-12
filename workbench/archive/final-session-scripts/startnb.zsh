#!/bin/zsh
# Stop the head to head of the dropped blanket-ban arm and start the no-blind-portal seeds, detached.
T=~/.claude/jobs/e2109d93/tmp
python3 $T/killtree.py "zsh $T/h2h16.zsh qbPA"
python3 $T/killtree.py "zsh $T/h2h16.zsh mHs15"
nohup zsh $T/nbtest.zsh > $T/nbtest.out 2>&1 &
sleep 3; cat $T/nbtest.out; pgrep -fl "tmp/nbtest" | cut -c1-80; date "+%H:%M:%S"
