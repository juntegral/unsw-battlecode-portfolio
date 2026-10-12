#!/bin/zsh
# mTd0 = one14 without TERRITORY_DECAY (the constant's default), from the candidate source; then queue its ladder-map check.
cd ~/meow-redteam/solo || exit 1
T=~/.claude/jobs/e2109d93/tmp
grep -n "constexpr.*TERRITORY_DECAY" src/w-one15/main.cpp
SW=$(sed 's/,TERRITORY_DECAY:16.0//' $T/one14.switches)
echo "$SW" | grep -c TERRITORY
MKSRC=src/w-one15/main.cpp python3 tools/mkbots.py "mTd0=$SW" 2>&1 | tail -n 1
shasum bots/mTd0/bot | cut -c1-12
nohup zsh $T/lcheck2.zsh mTd0 > /dev/null 2>&1 &
date "+%H:%M:%S"
