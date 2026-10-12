#!/bin/zsh
# w-one16 = orbit builder's source (candidate source + POCKET_PEARL_SKIP). Hash checks, then the arm mOrb.
cd ~/meow-redteam/solo || exit 1
T=~/.claude/jobs/e2109d93/tmp
mkdir -p src/w-one16
cp "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/orbit/main.cpp" src/w-one16/main.cpp
SW=$(cat $T/one14.switches)
MKSRC=src/w-one16/main.cpp python3 tools/mkbots.py "mOoff=" 2>&1 | tail -n 1
MKSRC=src/w-one16/main.cpp python3 tools/mkbots.py "mOliv=$SW" 2>&1 | tail -n 1
MKSRC=src/w-one16/main.cpp python3 tools/mkbots.py "mOrb4=$SW,POCKET_PEARL_SKIP:40" 2>&1 | tail -n 1
shasum bots/mOoff/bot bots/mOliv/bot bots/mNps/bot bots/mOrb4/bot | cut -c1-12,41-
date "+%H:%M:%S"
