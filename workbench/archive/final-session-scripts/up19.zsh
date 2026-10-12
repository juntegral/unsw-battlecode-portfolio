#!/bin/zsh
# one19 (last bot) = one18 - QUEEN_DEAD_ALL + CENTER_MAX_CELLS 100000 + QUEEN_NO_RAM + QUEEN_BLIND_STALL 20
# (source: w-one19 = team source + three switches, off by default; SPLIT_KNOWN_TAIL is in the file and stays off).
# Checks first: all-off hash; one18 values give the live binary; the one19 build equals the tested bot mC19.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
echo "diff against the team source: +$(diff src/solo/main.cpp src/w-one19/main.cpp | grep -c '^>') -$(diff src/solo/main.cpp src/w-one19/main.cpp | grep -c '^<')"
cp $T/one19C.switches $T/one19.switches
MKSRC=src/w-one19/main.cpp python3 tools/mkbots.py "mF19=" 2>&1 | tail -n 1
MKSRC=src/w-one19/main.cpp python3 tools/mkbots.py "mL19=$(cat $T/one18.switches)" 2>&1 | tail -n 1
MKSRC=src/w-one19/main.cpp python3 tools/mkbots.py "mD19=$(cat $T/one19.switches)" 2>&1 | tail -n 1
shasum bots/mF19/bot bots/mL19/bot bots/mD18/bot bots/mD19/bot bots/mC19/bot | cut -c1-12,41-
OFF=$(shasum bots/mF19/bot | cut -c1-12); LIV=$(shasum bots/mL19/bot | cut -c1-12); OLD=$(shasum bots/mD18/bot | cut -c1-12)
NEW=$(shasum bots/mD19/bot | cut -c1-12); TST=$(shasum bots/mC19/bot | cut -c1-12)
[ "$OFF" = "92fb69564fbd" ] && [ "$LIV" = "$OLD" ] && [ "$NEW" = "$TST" ] || { echo "CHECK FAILED, not uploading"; exit 1; }
cp src/solo/main.cpp src/solo/main.cpp.pre-one19-1009
cp src/w-one19/main.cpp src/solo/main.cpp
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
B=data/online/smoke
mkdir $B/one19-bot || exit 1
cp ~/meow-redteam/solo/bots/mD19/main.cpp ~/meow-redteam/solo/bots/mD19/helper.hpp ~/meow-redteam/solo/bots/mD19/sonar_codec.hpp $B/one19-bot/
cp $B/agg8-bot/bot.toml $B/one19-bot/
diff $B/one18-bot/main.cpp $B/one19-bot/main.cpp | grep "^[<>] constexpr" | cut -c1-120
node tools/submit.js upload "$PWD/$B/one19-bot" --name one19 --desc "one18 - QUEEN_DEAD_ALL (queen dead-end terms on small maps locked the side into start boxes) + CENTER_MAX_CELLS 100000 (start rooms on long maps over 1000 cells) + QUEEN_NO_RAM (a trapped queen no longer rams) + QUEEN_BLIND_STALL 20" --confirm --allow-pending 2>&1 | grep -v "unswbc\|pip install" | tail -n 2 | cut -c1-160
node tools/submit.js check "$PWD/$B/one19-bot" 2>&1 | grep "active" | cut -c1-100
ID=$(node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}')
echo "active id $ID"
printf '%s\tone19\n' "$ID" >> $B/versions.tsv
date "+%H:%M:%S"
