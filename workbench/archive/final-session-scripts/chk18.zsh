#!/bin/zsh
# Lead's own check of a builder's source: chk18.zsh <source file> <tag> <extra switches>
# Prints the size of its diff against the team source, then builds all-off, the live values, and live + the extra switches.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
SRC=$1; TAG=$2; EXTRA=$3
echo "diff lines against the team source: +$(diff src/solo/main.cpp $SRC | grep -c '^>') -$(diff src/solo/main.cpp $SRC | grep -c '^<')"
diff src/solo/main.cpp $SRC | grep "^> constexpr" | cut -c1-120
SW=$(cat $T/one17.switches)
MKSRC=$SRC python3 tools/mkbots.py "c${TAG}off=" 2>&1 | tail -n 1
MKSRC=$SRC python3 tools/mkbots.py "c${TAG}liv=$SW" 2>&1 | tail -n 1
MKSRC=$SRC python3 tools/mkbots.py "c${TAG}on=$SW,$EXTRA" 2>&1 | tail -n 1
shasum bots/c${TAG}off/bot bots/c${TAG}liv/bot bots/mD17/bot bots/c${TAG}on/bot | cut -c1-12,41-
date "+%H:%M:%S"
