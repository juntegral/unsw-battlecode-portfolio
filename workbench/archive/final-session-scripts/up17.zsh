#!/bin/zsh
# one17 = one16 + QS_SHED_MAX 9 (source: w-shed = team source + one constant and one condition).
# Checks first: small additive diff; all-off hash; one16 values give the live binary; the one17 build equals the tested bot mSh9.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
diff src/solo/main.cpp src/w-shed/main.cpp | grep "^[<>]" | cut -c1-170
printf '%s,QS_SHED_MAX:9\n' "$(cat $T/one16.switches)" > $T/one17.switches
MKSRC=src/w-shed/main.cpp python3 tools/mkbots.py "mF17=" 2>&1 | tail -n 1
MKSRC=src/w-shed/main.cpp python3 tools/mkbots.py "mL17=$(cat $T/one16.switches)" 2>&1 | tail -n 1
MKSRC=src/w-shed/main.cpp python3 tools/mkbots.py "mD17=$(cat $T/one17.switches)" 2>&1 | tail -n 1
shasum bots/mF17/bot bots/mL17/bot bots/mD16/bot bots/mD17/bot bots/mSh9/bot | cut -c1-12,41-
OFF=$(shasum bots/mF17/bot | cut -c1-12); LIV=$(shasum bots/mL17/bot | cut -c1-12); OLD=$(shasum bots/mD16/bot | cut -c1-12)
NEW=$(shasum bots/mD17/bot | cut -c1-12); TST=$(shasum bots/mSh9/bot | cut -c1-12)
[ "$OFF" = "92fb69564fbd" ] && [ "$LIV" = "$OLD" ] && [ "$NEW" = "$TST" ] || { echo "CHECK FAILED, not uploading"; exit 1; }
cp src/solo/main.cpp src/solo/main.cpp.pre-one17-1009
cp src/w-shed/main.cpp src/solo/main.cpp
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
B=data/online/smoke
mkdir $B/one17-bot || exit 1
cp ~/meow-redteam/solo/bots/mD17/main.cpp ~/meow-redteam/solo/bots/mD17/helper.hpp ~/meow-redteam/solo/bots/mD17/sonar_codec.hpp $B/one17-bot/
cp $B/agg8-bot/bot.toml $B/one17-bot/
diff $B/one16-bot/main.cpp $B/one17-bot/main.cpp | grep "^[<>]" | cut -c1-170
node tools/submit.js upload "$PWD/$B/one17-bot" --name one17 --desc "one16 + QS_SHED_MAX 9: a queen of 10 or longer no longer splits down to 2 when she sees no escape (21 such splits in 474 games, 18 lost, 15 while she led the queen race)" --confirm --allow-pending 2>&1 | grep -v "unswbc\|pip install" | tail -n 2 | cut -c1-160
node tools/submit.js check "$PWD/$B/one17-bot" 2>&1 | grep "active" | cut -c1-100
ID=$(node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}')
echo "active id $ID"
printf '%s\tone17\n' "$ID" >> $B/versions.tsv
date "+%H:%M:%S"
