#!/bin/zsh
# exp/portals v2 confirmation (PLAN-v2.md): W1 (var/w1-pocket) and V7 (var/v7-full2, the build of the v1 confirmation) on fresh seeds 51-70,
# proxy4_swarm / proxy4_king, both sides, 80 games each, 3 at a time, nice 10; stop below 21 GB free
cd "$(dirname "$0")/../.."
S=$(seq -s, 51 70 | sed 's/,$//')
run() { while [ $(df -g . | awk 'NR==2 {print $4}') -lt 21 ]; do sleep 60; done; nice -n 10 node tools/eval.js --bot $1 --label $2 --out $3 --opps proxy4_swarm,proxy4_king --seeds $S --maps exp/portals/maps-portals --jobs 3 > $3.log 2>&1; }
run exp/portals/var/w1-pocket pt-c2-w1 exp/portals/runs/c2-w1
run exp/portals/var/v7-full2 pt-c2-v7 exp/portals/runs/c2-v7
echo "$(date +%T) v2 confirmation done" >> exp/portals/runs/screen.log
