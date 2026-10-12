#!/bin/zsh
# What is loading the machine: the top CPU users and counts of game and analysis processes.
date "+%H:%M:%S"; uptime | sed 's/.*load/load/'
echo "play.sh: $(pgrep -f 'play.sh' | wc -l | tr -d ' ')  bot binaries: $(pgrep -f '/bot$' | wc -l | tr -d ' ')  python: $(pgrep -f 'python' | wc -l | tr -d ' ')  codex: $(pgrep -f 'codex' | wc -l | tr -d ' ')  c++/clang: $(pgrep -f 'clang|c\+\+' | wc -l | tr -d ' ')"
ps -Ao pcpu,pid,ppid,etime,command -r | head -n 25 | cut -c1-190
