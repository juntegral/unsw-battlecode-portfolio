#!/bin/zsh
# rerun of the missing half: new #30 bot vs dev1 (15 games, DEV allowance); the live half already exists in tc30-dev1
cd "~/01. Project/개인 프로젝트/unsw-swarm"
BOT="~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/tc30-bot"
echo "$(date '+%F %T') starting tc30-dev1b (new bot only vs 545)" >> data/online/smoke/at-tc30.log
data/online/smoke/run-pair.sh tc30-dev1b "$BOT" "#30 big-map-trades vs dev1" 545
P=$(python3 -c "import json;print(json.load(open('data/online/smoke/tc30-dev1b.json')).get('phase'))" 2>/dev/null || echo none)
echo "$(date '+%F %T') tc30-dev1b ended; phase: $P" >> data/online/smoke/at-tc30.log
[ "$P" = "rolled-back" ] && python3 tools/pair_report.py tc30-dev1b --post "#30 big-map-trades vs dev1" > data/online/smoke/tc30-dev1b-report.log 2>&1
echo "$(date '+%F %T') dev1b done" >> data/online/smoke/at-tc30.log
