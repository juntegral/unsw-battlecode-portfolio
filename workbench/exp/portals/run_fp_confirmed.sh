#!/bin/zsh
# exp/portals: the build the confirmation ran with (var/v7-full2) against the final cleaned module (bot/) on Portals, 3 seeds x 2 opponents
cd "$(dirname "$0")/../.."
O=exp/portals/identity/confirmed-build.txt; : > $O
for opp in bots/proxy4_king bots/proxy4_swarm; do for s in 1 2 3; do
  echo "== var/v7-full2 vs bot, $opp seed $s" >> $O; nice -n 10 node tools/fingerprint.js --same exp/portals/var/v7-full2 exp/portals/bot --maps portals --opp $opp --seed $s >> $O 2>&1
done; done
echo done >> $O
