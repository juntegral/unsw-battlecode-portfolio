#!/bin/zsh
# Integration source for the last bot: w-one19 = team source (one18) + QUEEN_NO_RAM (lead, 3 lines) + SPLIT_KNOWN_TAIL
# (trauma builder's 2-hunk diff). Check: all-off hash, one18 values give the live binary. Then list the diff.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
mkdir -p src/w-one19
cp src/w-noram/main.cpp src/w-one19/main.cpp
patch -s src/w-one19/main.cpp < "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/trauma-opus/trauma-opus.diff"; echo "patch rc $?"
ls src/w-one19 | tr '\n' ' '; echo
diff src/solo/main.cpp src/w-one19/main.cpp | grep "^[<>]" | cut -c1-190
MKSRC=src/w-one19/main.cpp python3 tools/mkbots.py "mF19=" 2>&1 | tail -n 1
MKSRC=src/w-one19/main.cpp python3 tools/mkbots.py "mL19=$(cat $T/one18.switches)" 2>&1 | tail -n 1
shasum bots/mF19/bot bots/mL19/bot bots/mD18/bot | cut -c1-12,41-
date "+%H:%M:%S"
