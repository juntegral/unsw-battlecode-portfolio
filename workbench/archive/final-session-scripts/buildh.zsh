#!/bin/zsh
# Integration source w-one15 = the hidden builder's source; build all-off (hash check) and one14 + THREAT_HIDDEN_PARTS 8.
cd ~/meow-redteam/solo || exit 1
mkdir -p src/w-one15
cp "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/hidden/main.cpp" src/w-one15/main.cpp
SW=$(cat ~/.claude/jobs/e2109d93/tmp/one14.switches)
MKSRC=src/w-one15/main.cpp python3 tools/mkbots.py "mHoff=" 2>&1 | tail -n 1
MKSRC=src/w-one15/main.cpp python3 tools/mkbots.py "mHliv=$SW" 2>&1 | tail -n 1
MKSRC=src/w-one15/main.cpp python3 tools/mkbots.py "mHid8=$SW,THREAT_HIDDEN_PARTS:8" 2>&1 | tail -n 1
shasum bots/mHoff/bot bots/mSolo/bot bots/mHliv/bot bots/mNps/bot bots/mHid8/bot | cut -c1-12,41-
date "+%H:%M:%S"
