#!/bin/zsh
# one18 = one17 + QUEEN_CORRIDOR_MATE true (source: w-qtrap = team source + 23 lines, two switches off by default).
# Checks first: all-off hash; one17 values give the live binary; the one18 build equals the tested bot qtm.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
echo "diff against the team source: +$(diff src/solo/main.cpp src/w-qtrap/main.cpp | grep -c '^>') -$(diff src/solo/main.cpp src/w-qtrap/main.cpp | grep -c '^<')"
printf '%s,QUEEN_CORRIDOR_MATE:true\n' "$(cat $T/one17.switches)" > $T/one18.switches
MKSRC=src/w-qtrap/main.cpp python3 tools/mkbots.py "mF18=" 2>&1 | tail -n 1
MKSRC=src/w-qtrap/main.cpp python3 tools/mkbots.py "mL18=$(cat $T/one17.switches)" 2>&1 | tail -n 1
MKSRC=src/w-qtrap/main.cpp python3 tools/mkbots.py "mD18=$(cat $T/one18.switches)" 2>&1 | tail -n 1
shasum bots/mF18/bot bots/mL18/bot bots/mD17/bot bots/mD18/bot bots/qtm/bot | cut -c1-12,41-
OFF=$(shasum bots/mF18/bot | cut -c1-12); LIV=$(shasum bots/mL18/bot | cut -c1-12); OLD=$(shasum bots/mD17/bot | cut -c1-12)
NEW=$(shasum bots/mD18/bot | cut -c1-12); TST=$(shasum bots/qtm/bot | cut -c1-12)
[ "$OFF" = "92fb69564fbd" ] && [ "$LIV" = "$OLD" ] && [ "$NEW" = "$TST" ] || { echo "CHECK FAILED, not uploading"; exit 1; }
cp src/solo/main.cpp src/solo/main.cpp.pre-one18-1009
cp src/w-qtrap/main.cpp src/solo/main.cpp
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
B=data/online/smoke
mkdir $B/one18-bot || exit 1
cp ~/meow-redteam/solo/bots/mD18/main.cpp ~/meow-redteam/solo/bots/mD18/helper.hpp ~/meow-redteam/solo/bots/mD18/sonar_codec.hpp $B/one18-bot/
cp $B/agg8-bot/bot.toml $B/one18-bot/
diff $B/one17-bot/main.cpp $B/one18-bot/main.cpp | grep -c "^[<>]"
node tools/submit.js upload "$PWD/$B/one18-bot" --name one18 --desc "one17 + QUEEN_CORRIDOR_MATE: when the queen's corridor guard has judged her move a dead end and found no clean other step, it looks again with mates' bodies as passable instead of keeping the fatal step (three Maze games thrown from a lead this way)" --confirm --allow-pending 2>&1 | grep -v "unswbc\|pip install" | tail -n 2 | cut -c1-160
node tools/submit.js check "$PWD/$B/one18-bot" 2>&1 | grep "active" | cut -c1-100
ID=$(node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}')
echo "active id $ID"
printf '%s\tone18\n' "$ID" >> $B/versions.tsv
date "+%H:%M:%S"
