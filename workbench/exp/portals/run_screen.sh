#!/bin/zsh
# exp/portals: the screen (PLAN.md): each variant on proxy4_swarm / proxy4_king, sides A / B, seeds 1-10, 3 games at a time, nice 10.
cd "$(dirname "$0")/../.."
for v in "$@"; do
  while [ $(df -g . | awk 'NR==2 {print $4}') -lt 20 ]; do echo "$(date +%T) disk < 20G, waiting" >> exp/portals/runs/pause.log; sleep 60; done
  nice -n 10 node tools/eval.js --bot exp/portals/var/$v --label pt-$v --out exp/portals/runs/$v --opps proxy4_swarm,proxy4_king --seeds 1,2,3,4,5,6,7,8,9,10 --maps exp/portals/maps-portals --jobs 3 > exp/portals/runs/$v.log 2>&1
  echo "$(date +%T) done $v" >> exp/portals/runs/screen.log
done
