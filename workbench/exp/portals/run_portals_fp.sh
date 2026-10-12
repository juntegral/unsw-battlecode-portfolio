#!/bin/zsh
# exp/portals: Portals event-stream identity checks (tools/fingerprint.js), one game at a time, nice 10:
#   1. bot-base vs bot-head  (did v1 final change our Portals play?)          seeds 1, 2, 3 vs proxy4_king and proxy4_swarm
#   2. bot vs bot-v11         (does the rebased module play as the measured one?)
#   3. var/v9-late or var/v7-final vs bot (the cleaned code plays as the variant that ran; set by the argument)
cd "$(dirname "$0")/../.."
O=exp/portals/identity/portals.txt; : > $O
for opp in bots/proxy4_king bots/proxy4_swarm; do for s in 1 2 3; do
  echo "== base vs head, $opp seed $s" >> $O; nice -n 10 node tools/fingerprint.js --same exp/portals/bot-base exp/portals/bot-head --maps portals --opp $opp --seed $s >> $O 2>&1
  echo "== bot vs bot-v11, $opp seed $s" >> $O; nice -n 10 node tools/fingerprint.js --same exp/portals/bot exp/portals/bot-v11 --maps portals --opp $opp --seed $s >> $O 2>&1
  echo "== $1 vs bot, $opp seed $s" >> $O; nice -n 10 node tools/fingerprint.js --same exp/portals/var/$1 exp/portals/bot --maps portals --opp $opp --seed $s >> $O 2>&1
done; done
echo done >> $O
