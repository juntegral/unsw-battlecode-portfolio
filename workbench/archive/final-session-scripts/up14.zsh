#!/bin/zsh
# Upload one14 = one13 with PORTAL_SCOUT_MIN_LEN 0 (local arm mNps), verify, record its id.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
B=data/online/smoke
mkdir $B/one14-bot || exit 1
cp ~/meow-redteam/solo/bots/mNps/main.cpp ~/meow-redteam/solo/bots/mNps/helper.hpp ~/meow-redteam/solo/bots/mNps/sonar_codec.hpp $B/one14-bot/
cp $B/agg8-bot/bot.toml $B/one14-bot/
c++ -std=c++20 -O2 $B/one14-bot/main.cpp -o ~/.claude/jobs/e2109d93/tmp/one14.bin && echo compiled
diff $B/one13-bot/main.cpp $B/one14-bot/main.cpp
node tools/submit.js upload "$PWD/$B/one14-bot" --name one14 --desc "one13 with PORTAL_SCOUT_MIN_LEN 0: the short-dragon portal rule kept the whole side out of portals and starved it on portal maps" --confirm --allow-pending 2>&1 | grep -v "unswbc\|pip install" | tail -n 2 | cut -c1-160
node tools/submit.js check "$PWD/$B/one14-bot" 2>&1 | grep "active" | cut -c1-100
ID=$(node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}')
echo "active id $ID"
printf '%s\tone14\n' "$ID" >> $B/versions.tsv
date "+%H:%M:%S"
