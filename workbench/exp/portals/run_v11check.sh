#!/bin/zsh
# exp/portals: the module on top of v1.1 (versions/v1.1/bot at d347ef6 = exp/portals/bot-v11base, with the king beacon) against v1.1 itself,
# Portals seeds 1-10, proxy4_swarm / proxy4_king, both sides; after the identity runs (at most 3 games at a time), nice 10.
cd "$(dirname "$0")/../.."
done_id() { for f in head-seed1 head-seed2 orig-seed1 orig-seed2; do grep -q "^exit" exp/portals/identity/$f.txt 2>/dev/null || return 1; done; return 0; }
until done_id && ! pgrep -f "fingerprint.js --same exp/portals" > /dev/null; do sleep 15; done
S=1,2,3,4,5,6,7,8,9,10
nice -n 10 node tools/eval.js --bot exp/portals/bot-v11base --label pt-v11base --out exp/portals/runs/v11base --opps proxy4_swarm,proxy4_king --seeds $S --maps exp/portals/maps-portals --jobs 3 > exp/portals/runs/v11base.log 2>&1
nice -n 10 node tools/eval.js --bot exp/portals/bot-v111 --label pt-v111 --out exp/portals/runs/v111 --opps proxy4_swarm,proxy4_king --seeds $S --maps exp/portals/maps-portals --jobs 3 > exp/portals/runs/v111.log 2>&1
echo "$(date +%T) v1.1 check done" >> exp/portals/runs/screen.log
