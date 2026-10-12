#!/bin/zsh
# one20 (last bot) = one18 - QUEEN_DEAD_ALL + CENTER_MAX_CELLS 100000 + QUEEN_NO_RAM + QUEEN_BLIND_STALL 20
# (source: w-one20 = team source + three switches, off by default; SPLIT_KNOWN_TAIL is in the file and stays off).
# Checks first: all-off hash; one18 values give the live binary; the one20 build equals the tested bot mD20.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
echo "diff against the team source: +$(diff src/solo/main.cpp src/w-one20/main.cpp | grep -c '^>') -$(diff src/solo/main.cpp src/w-one20/main.cpp | grep -c '^<')"
cp $T/one19.switches $T/one20.switches
MKSRC=src/w-one20/main.cpp python3 tools/mkbots.py "mF20=" 2>&1 | tail -n 1
MKSRC=src/w-one20/main.cpp python3 tools/mkbots.py "mL20=$(cat $T/one18.switches)" 2>&1 | tail -n 1
MKSRC=src/w-one20/main.cpp python3 tools/mkbots.py "mE20=$(cat $T/one20.switches)" 2>&1 | tail -n 1
shasum bots/mF20/bot bots/mL20/bot bots/mD18/bot bots/mE20/bot bots/mD20/bot | cut -c1-12,41-
OFF=$(shasum bots/mF20/bot | cut -c1-12); LIV=$(shasum bots/mL20/bot | cut -c1-12); OLD=$(shasum bots/mD18/bot | cut -c1-12)
NEW=$(shasum bots/mE20/bot | cut -c1-12); TST=$(shasum bots/mD20/bot | cut -c1-12)
[ "$OFF" = "92fb69564fbd" ] && [ "$LIV" = "$OLD" ] && [ "$NEW" = "$TST" ] || { echo "CHECK FAILED, not uploading"; exit 1; }
cp src/solo/main.cpp src/solo/main.cpp.pre-one20-1009
cp src/w-one20/main.cpp src/solo/main.cpp
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
B=data/online/smoke
mkdir $B/one20-bot || exit 1
cp ~/meow-redteam/solo/bots/mE20/main.cpp ~/meow-redteam/solo/bots/mE20/helper.hpp ~/meow-redteam/solo/bots/mE20/sonar_codec.hpp $B/one20-bot/
cp $B/agg8-bot/bot.toml $B/one20-bot/
diff $B/one18-bot/main.cpp $B/one20-bot/main.cpp | grep "^[<>] constexpr" | cut -c1-120
node tools/submit.js upload "$PWD/$B/one20-bot" --name one20 --desc "one19 with two completions: a trapped queen under QUEEN_NO_RAM no longer marks trade or hunt targets, and QUEEN_BLIND_STALL only acts between round 20 and 100" --confirm --allow-pending 2>&1 | grep -v "unswbc\|pip install" | tail -n 2 | cut -c1-160
node tools/submit.js check "$PWD/$B/one20-bot" 2>&1 | grep "active" | cut -c1-100
ID=$(node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}')
echo "active id $ID"
printf '%s\tone20\n' "$ID" >> $B/versions.tsv
date "+%H:%M:%S"
