#!/bin/zsh
# exp/portals: V9 against V7 (the cleaned bot, late room rule off) on fresh seeds 31-50 (PLAN.md amendment 05:12)
cd "$(dirname "$0")/../.."
while pgrep -f "eval.js --bot exp/portals" > /dev/null; do sleep 10; done
S=$(seq -s, 31 50 | sed 's/,$//')
run() { while [ $(df -g . | awk 'NR==2 {print $4}') -lt 20 ]; do sleep 60; done; nice -n 10 node tools/eval.js --bot $1 --label $2 --out $3 --opps proxy4_swarm,proxy4_king --seeds $S --maps exp/portals/maps-portals --jobs 3 > $3.log 2>&1; }
run exp/portals/var/v7-final pt-fin-v7 exp/portals/runs/fin-v7
run exp/portals/var/v9-late pt-fin-v9 exp/portals/runs/fin-v9
echo "$(date +%T) final done" >> exp/portals/runs/screen.log
