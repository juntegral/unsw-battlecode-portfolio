#!/bin/zsh
# Stop the exploration-pull batch (the arm failed in the builder's own tests). Build one15-based arms and start their checks:
# mHs15 = one15 + HARVEST_SPLIT true; mQ15 = one15 + QS_HEAD_CLEAR 4; mO15 = one15 + POCKET_PEARL_SKIP 40.
T=~/.claude/jobs/e2109d93/tmp
python3 $T/killtree.py "zsh $T/lcheck2b.zsh mEx10 mEx05"
cd ~/meow-redteam/solo || exit 1
grep -n "constexpr.*HARVEST_SPLIT" src/w-one16/main.cpp
SW=$(cat $T/one15.switches)
MKSRC=src/w-one16/main.cpp python3 tools/mkbots.py "mHs15=$SW,HARVEST_SPLIT:true" 2>&1 | tail -n 1
MKSRC=src/w-one16/main.cpp python3 tools/mkbots.py "mQ15=$SW,QS_HEAD_CLEAR:4" 2>&1 | tail -n 1
MKSRC=src/w-one16/main.cpp python3 tools/mkbots.py "mO15=$SW,POCKET_PEARL_SKIP:40" 2>&1 | tail -n 1
shasum bots/mHs15/bot bots/mQ15/bot bots/mO15/bot | cut -c1-12,41-
LC_P=6 nohup zsh $T/lcheck2b.zsh mHs15 > /dev/null 2>&1 &
sleep 1; pgrep -fl "tmp/lcheck2b|tmp/h2h15|tmp/lcchain" | cut -c1-110
date "+%H:%M:%S"; uptime | sed 's/.*load/load/'
