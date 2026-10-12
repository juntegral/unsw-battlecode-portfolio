#!/bin/zsh
# Arms mEx10 / mEx05 = one14 + EXPLORE_GAIN 10 / 5 (an existing constant), from the candidate source; then their ladder-map check.
cd ~/meow-redteam/solo || exit 1
T=~/.claude/jobs/e2109d93/tmp
grep -n "constexpr.*EXPLORE_GAIN" src/w-one16/main.cpp
SW=$(cat $T/one14.switches)
MKSRC=src/w-one16/main.cpp python3 tools/mkbots.py "mEx10=$SW,EXPLORE_GAIN:10" 2>&1 | tail -n 1
MKSRC=src/w-one16/main.cpp python3 tools/mkbots.py "mEx05=$SW,EXPLORE_GAIN:5" 2>&1 | tail -n 1
shasum bots/mEx10/bot bots/mEx05/bot | cut -c1-12,41-
LC_P=6 nohup zsh $T/lcheck2b.zsh mEx10 mEx05 > /dev/null 2>&1 &
sleep 1; pgrep -fl "tmp/lcheck2b" | cut -c1-120
date "+%H:%M:%S"
