#!/bin/zsh
# one16 = one15 + QUEEN_NO_BLIND_PORTAL true (source: the qbox builder's file = team source + one switch).
# Checks first: the diff against the team source is small and only adds; all-off hash; one15 values give the live binary;
# the one16 build equals the bot the tests were played with. Then promote the source, upload, verify.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
diff src/solo/main.cpp src/w-qbox/main.cpp | grep -c "^[<>]"
diff src/solo/main.cpp src/w-qbox/main.cpp | grep "^[<>]" | cut -c1-150
printf '%s,QUEEN_NO_BLIND_PORTAL:true\n' "$(cat $T/one15.switches)" > $T/one16.switches
MKSRC=src/w-qbox/main.cpp python3 tools/mkbots.py "mF16=" 2>&1 | tail -n 1
MKSRC=src/w-qbox/main.cpp python3 tools/mkbots.py "mL16=$(cat $T/one15.switches)" 2>&1 | tail -n 1
MKSRC=src/w-qbox/main.cpp python3 tools/mkbots.py "mD16=$(cat $T/one16.switches)" 2>&1 | tail -n 1
shasum bots/mF16/bot bots/mL16/bot bots/mD15/bot bots/mD16/bot bots/qbNB/bot | cut -c1-12,41-
OFF=$(shasum bots/mF16/bot | cut -c1-12); LIV=$(shasum bots/mL16/bot | cut -c1-12); OLD=$(shasum bots/mD15/bot | cut -c1-12)
NEW=$(shasum bots/mD16/bot | cut -c1-12); TST=$(shasum bots/qbNB/bot | cut -c1-12)
[ "$OFF" = "92fb69564fbd" ] && [ "$LIV" = "$OLD" ] && [ "$NEW" = "$TST" ] || { echo "CHECK FAILED, not uploading"; exit 1; }
cp src/solo/main.cpp src/solo/main.cpp.pre-one16-1009
cp src/w-qbox/main.cpp src/solo/main.cpp
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
B=data/online/smoke
mkdir $B/one16-bot || exit 1
cp ~/meow-redteam/solo/bots/mD16/main.cpp ~/meow-redteam/solo/bots/mD16/helper.hpp ~/meow-redteam/solo/bots/mD16/sonar_codec.hpp $B/one16-bot/
cp $B/agg8-bot/bot.toml $B/one16-bot/
node tools/submit.js upload "$PWD/$B/one16-bot" --name one16 --desc "one15 + QUEEN_NO_BLIND_PORTAL: on maps of 600 cells or fewer the queen no longer steps through a portal whose far side nobody has seen" --confirm --allow-pending 2>&1 | grep -v "unswbc\|pip install" | tail -n 2 | cut -c1-160
node tools/submit.js check "$PWD/$B/one16-bot" 2>&1 | grep "active" | cut -c1-100
ID=$(node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}')
echo "active id $ID"
printf '%s\tone16\n' "$ID" >> $B/versions.tsv
date "+%H:%M:%S"
