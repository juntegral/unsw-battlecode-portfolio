#!/bin/zsh
# exp/portals v2 screen (PLAN-v2.md): seeds 1-10, proxy4_swarm / proxy4_king, both sides, 3 games at a time, nice 10; stop below 21 GB free
cd "$(dirname "$0")/../.."
for v in "$@"; do
  while [ $(df -g . | awk 'NR==2 {print $4}') -lt 21 ]; do echo "$(date +%T) disk < 21G, waiting" >> exp/portals/runs/pause.log; sleep 60; done
  nice -n 10 node tools/eval.js --bot exp/portals/var/$v --label pt-$v --out exp/portals/runs/$v --opps proxy4_swarm,proxy4_king --seeds 1,2,3,4,5,6,7,8,9,10 --maps exp/portals/maps-portals --jobs 3 > exp/portals/runs/$v.log 2>&1
  echo "$(date +%T) done $v" >> exp/portals/runs/screen.log
done
