#!/bin/zsh
# exp/portals v2 verification (at most 3 games at a time, nice 10):
#   slot 1: Portals fingerprints, var/w1-pocket (the confirmed build) vs bot3 (the cleaned v2), 3 seeds x 2 opponents; then orig identity seed 1
#   slot 2: v1.2 identity seed 1 (bot-v12base vs bot3-v12, the other 9 maps); then orig identity seed 2
#   slot 3: v1.2 identity seed 2
cd "$(dirname "$0")/../.."
M=autarky,default,devil,prisoners_dilemma,queen_of_spades,schooltime,slithery_fight,trauma,trophy
mkdir -p exp/portals/identity
fp() { nice -n 10 node tools/fingerprint.js --same $1 $2 --maps $3 --seed $4 ${5:+--opp $5} >> $6 2>&1; }
(
  O=exp/portals/identity/v2-confirmed-build.txt; : > $O
  for opp in bots/proxy4_king bots/proxy4_swarm; do for s in 1 2 3; do echo "== var/w1-pocket vs bot3, $opp seed $s" >> $O; fp exp/portals/var/w1-pocket exp/portals/bot3 portals $s $opp $O; done; done; echo done >> $O
  O=exp/portals/identity/v2-orig-seed1.txt; : > $O; fp exp/portals/bot-base exp/portals/bot3 $M 1 "" $O; echo "exit $?" >> $O
) &
(
  O=exp/portals/identity/v2-v12-seed1.txt; : > $O; fp exp/portals/bot-v12base exp/portals/bot3-v12 $M 1 "" $O; echo "exit $?" >> $O
  O=exp/portals/identity/v2-orig-seed2.txt; : > $O; fp exp/portals/bot-base exp/portals/bot3 $M 2 "" $O; echo "exit $?" >> $O
) &
(
  O=exp/portals/identity/v2-v12-seed2.txt; : > $O; fp exp/portals/bot-v12base exp/portals/bot3-v12 $M 2 "" $O; echo "exit $?" >> $O
) &
wait
echo "$(date +%T) v2 verify done" >> exp/portals/runs/screen.log
