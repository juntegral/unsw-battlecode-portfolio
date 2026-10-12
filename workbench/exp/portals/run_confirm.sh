#!/bin/zsh
# exp/portals: confirmation on fresh seeds (PLAN.md amendment 04:48): the two candidates on seeds 11-30 and the baseline on the same keys
# (runs/base already holds seeds 1-15). proxy4_swarm / proxy4_king, sides A / B, 3 games at a time, nice 10.
cd "$(dirname "$0")/../.."
S=$(seq -s, 11 30 | sed 's/,$//')
S2=$(seq -s, 16 30 | sed 's/,$//')
run() { while [ $(df -g . | awk 'NR==2 {print $4}') -lt 20 ]; do sleep 60; done; nice -n 10 node tools/eval.js --bot $1 --label $2 --out $3 --opps proxy4_swarm,proxy4_king --seeds $4 --maps exp/portals/maps-portals --jobs 3 > $3.log 2>&1; }
run exp/portals/var/v7-full2 pt-conf-v7 exp/portals/runs/conf-v7 $S
run exp/portals/var/v8-clock2 pt-conf-v8 exp/portals/runs/conf-v8 $S
run exp/portals/bot-base pt-base exp/portals/runs/base $S2
echo "$(date +%T) confirm done" >> exp/portals/runs/screen.log
