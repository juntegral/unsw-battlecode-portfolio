#!/bin/zsh
# w-one15 = hidden builder's source + qsnear diff. Build all-off, live (one14 values), and the two candidates.
cd ~/meow-redteam/solo || exit 1
B="~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build"
ls src/w-one15/ | tr '\n' ' '; echo
grep -n "constexpr.*QS_HEAD_CLEAR\|constexpr.*THREAT_HIDDEN_PARTS\|constexpr.*THREAT_SEEN_SIZE" src/w-one15/main.cpp
SW=$(cat ~/.claude/jobs/e2109d93/tmp/one14.switches)
MKSRC=src/w-one15/main.cpp python3 tools/mkbots.py "mHoff=" 2>&1 | tail -n 1
MKSRC=src/w-one15/main.cpp python3 tools/mkbots.py "mHliv=$SW" 2>&1 | tail -n 1
MKSRC=src/w-one15/main.cpp python3 tools/mkbots.py "mHid8=$SW,THREAT_HIDDEN_PARTS:8" 2>&1 | tail -n 1
MKSRC=src/w-one15/main.cpp python3 tools/mkbots.py "mQsn4=$SW,QS_HEAD_CLEAR:4" 2>&1 | tail -n 1
MKSRC=src/w-one15/main.cpp python3 tools/mkbots.py "mBoth=$SW,THREAT_HIDDEN_PARTS:8,QS_HEAD_CLEAR:4" 2>&1 | tail -n 1
shasum bots/mHoff/bot bots/mHliv/bot bots/mNps/bot bots/mHid8/bot bots/mQsn4/bot bots/mBoth/bot | cut -c1-12,41-
date "+%H:%M:%S"
