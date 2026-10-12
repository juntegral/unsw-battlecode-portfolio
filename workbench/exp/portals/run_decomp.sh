#!/bin/zsh
# exp/portals: decomposition after the decision (team lead 06:00): LEN only and V7 without LEN on the confirmation keys (seeds 11-30,
# 80 games each), then the null module against bot-base on Portals (fingerprints). 3 games at a time, nice 10.
cd "$(dirname "$0")/../.."
until grep -q "^done" exp/portals/identity/confirmed-build.txt 2>/dev/null; do sleep 10; done
S=$(seq -s, 11 30 | sed 's/,$//')
run() { while [ $(df -g . | awk 'NR==2 {print $4}') -lt 20 ]; do sleep 60; done; nice -n 10 node tools/eval.js --bot exp/portals/var/$1 --label pt-$1 --out exp/portals/runs/$1 --opps proxy4_swarm,proxy4_king --seeds $S --maps exp/portals/maps-portals --jobs 3 > exp/portals/runs/$1.log 2>&1; }
run d-lenonly
run d-nolen
O=exp/portals/identity/null-module.txt; : > $O
for opp in bots/proxy4_king bots/proxy4_swarm; do for s in 1 2 3; do
  echo "== bot-base vs var/d-null, $opp seed $s" >> $O; nice -n 10 node tools/fingerprint.js --same exp/portals/bot-base exp/portals/var/d-null --maps portals --opp $opp --seed $s >> $O 2>&1
done; done
echo done >> $O
echo "$(date +%T) decomposition done" >> exp/portals/runs/screen.log
