#!/bin/zsh
# one21 = one20 + QS_LONG_WAIT true (Zhe's last feedback: an exposed long queen with no escape stays and splits off 2 cells
# instead of stepping into a tile an enemy can reach). Checks: all-off hash, one18 values = live one18 binary, the one20
# values without the new switch = the live one20 binary; four short games must finish with a result. Then upload.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
echo "diff against the team source: +$(diff src/solo/main.cpp src/w-one21/main.cpp | grep -c '^>') -$(diff src/solo/main.cpp src/w-one21/main.cpp | grep -c '^<')"
printf '%s,QS_LONG_WAIT:true\n' "$(cat $T/one20.switches)" > $T/one21.switches
MKSRC=src/w-one21/main.cpp python3 tools/mkbots.py "mF21=" 2>&1 | tail -n 1
MKSRC=src/w-one21/main.cpp python3 tools/mkbots.py "mL21=$(cat $T/one20.switches)" 2>&1 | tail -n 1
MKSRC=src/w-one21/main.cpp python3 tools/mkbots.py "mD21=$(cat $T/one21.switches)" 2>&1 | tail -n 1
shasum bots/mF21/bot bots/mL21/bot bots/mD20/bot bots/mD21/bot | cut -c1-12,41-
OFF=$(shasum bots/mF21/bot | cut -c1-12); LIV=$(shasum bots/mL21/bot | cut -c1-12); OLD=$(shasum bots/mD20/bot | cut -c1-12)
[ "$OFF" = "92fb69564fbd" ] && [ "$LIV" = "$OLD" ] || { echo "CHECK FAILED, not uploading"; exit 1; }
cd ~/meow-redteam || exit 1
for N in ladder_stripes_1 ladder_portals_1 ladder_devil_1 ladder_weakhold_1; do
  ./play.sh solo/bots/mD21 solo/bots/m3base maps/ladder/$N.map 1 solo/runs/nr_mD21/$N-seed1-side0 > /dev/null 2>&1 &
done
wait
OK=$(ls solo/runs/nr_mD21/*/result.txt 2>/dev/null | wc -l | tr -d ' ')
for N in ladder_stripes_1 ladder_portals_1 ladder_devil_1 ladder_weakhold_1; do echo "$N: $(cat solo/runs/nr_mD21/$N-seed1-side0/result.txt | tr '\n' ' ' | cut -c1-90) | one20: $(cat solo/runs/nr_mD20/$N-seed1-side0/result.txt | tr '\n' ' ' | cut -c1-90)"; done
[ "$OK" = "4" ] || { echo "GAMES DID NOT FINISH, not uploading"; exit 1; }
date "+%H:%M:%S"
cd ~/meow-redteam/solo || exit 1
cp src/solo/main.cpp src/solo/main.cpp.pre-one21-1009
cp src/w-one21/main.cpp src/solo/main.cpp
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
B=data/online/smoke
mkdir $B/one21-bot || exit 1
cp ~/meow-redteam/solo/bots/mD21/main.cpp ~/meow-redteam/solo/bots/mD21/helper.hpp ~/meow-redteam/solo/bots/mD21/sonar_codec.hpp $B/one21-bot/
cp $B/agg8-bot/bot.toml $B/one21-bot/
node tools/submit.js upload "$PWD/$B/one21-bot" --name one21 --desc "one20 + QS_LONG_WAIT: an exposed queen of 10 or longer with no escape stays and splits off 2 cells instead of stepping into a tile an enemy can reach (Zhe, match 1532574)" --confirm --allow-pending 2>&1 | grep -v "unswbc\|pip install" | tail -n 2 | cut -c1-160
node tools/submit.js check "$PWD/$B/one21-bot" 2>&1 | grep "active" | cut -c1-100
ID=$(node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}')
echo "active id $ID"
printf '%s\tone21\n' "$ID" >> $B/versions.tsv
date "+%H:%M:%S"
