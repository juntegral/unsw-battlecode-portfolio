#!/bin/zsh
# one15 = one14 without TERRITORY_DECAY. Build from the team source (src/solo), check it equals the tested arm mTd0, upload, verify.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
sed 's/,TERRITORY_DECAY:16.0//' $T/one14.switches > $T/one15.switches
grep -c "TERRITORY_DECAY" $T/one15.switches
MKSRC=src/solo/main.cpp python3 tools/mkbots.py "mD15=$(cat $T/one15.switches)" 2>&1 | tail -n 1
A=$(shasum bots/mD15/bot | cut -c1-12); B=$(shasum bots/mTd0/bot | cut -c1-12)
echo "mD15 $A  mTd0 $B"
[ "$A" = "$B" ] || { echo "HASH MISMATCH, not uploading"; exit 1; }
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
B=data/online/smoke
mkdir $B/one15-bot || exit 1
cp ~/meow-redteam/solo/bots/mD15/main.cpp ~/meow-redteam/solo/bots/mD15/helper.hpp ~/meow-redteam/solo/bots/mD15/sonar_codec.hpp $B/one15-bot/
cp $B/agg8-bot/bot.toml $B/one15-bot/
diff $B/one14-bot/main.cpp $B/one15-bot/main.cpp
node tools/submit.js upload "$PWD/$B/one15-bot" --name one15 --desc "one14 without TERRITORY_DECAY: with it our side starved on Queen Of Spades (pearls by r100 59 to 17 online, 8 to 44 locally with it removed)" --confirm --allow-pending 2>&1 | grep -v "unswbc\|pip install" | tail -n 2 | cut -c1-160
node tools/submit.js check "$PWD/$B/one15-bot" 2>&1 | grep "active" | cut -c1-100
ID=$(node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}')
echo "active id $ID"
printf '%s\tone15\n' "$ID" >> $B/versions.tsv
date "+%H:%M:%S"
