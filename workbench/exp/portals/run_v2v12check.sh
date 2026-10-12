#!/bin/zsh
# exp/portals v2: the v2 delta on top of v1.2 (versions/v1.2/bot at 91a1cca = bot-v12base, which already carries V7) against v1.2 itself,
# Portals, fresh seeds 71-80, proxy4_swarm / proxy4_king, both sides (40 games each); after the verification runs; 3 at a time, nice 10
cd "$(dirname "$0")/../.."
until grep -q "v2 verify done" exp/portals/runs/screen.log 2>/dev/null; do sleep 15; done
S=71,72,73,74,75,76,77,78,79,80
run() { while [ $(df -g . | awk 'NR==2 {print $4}') -lt 21 ]; do sleep 60; done; nice -n 10 node tools/eval.js --bot $1 --label $2 --out $3 --opps proxy4_swarm,proxy4_king --seeds $S --maps exp/portals/maps-portals --jobs 3 > $3.log 2>&1; }
run exp/portals/bot-v12base pt-v12base exp/portals/runs/v12base
run exp/portals/bot3-v12 pt-v12v2 exp/portals/runs/v12v2
echo "$(date +%T) v1.2 v2 check done" >> exp/portals/runs/screen.log
