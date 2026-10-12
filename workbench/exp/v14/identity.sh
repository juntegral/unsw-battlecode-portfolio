#!/bin/zsh
# v1.4 check (a): OPENING_ON = false (exp/v14/bot-opoff) against v1.2, 3 fortress + 3 swarm maps, seeds 1 and 2 (tools/fingerprint.js --same:
# our bot on side A against proxy4_king, one game at a time). Stops below 21 GB free.
cd "$(dirname "$0")/../.."
for s in 1 2; do
  [ "$(df -g / | awk 'NR==2 {print $4}')" -ge 21 ] || { echo "disk < 21 GB: stop"; exit 1; }
  nice -n 10 node tools/fingerprint.js --same versions/v1.2/bot exp/v14/bot-opoff --maps autarky,prisoners_dilemma,portals,devil,schooltime,slithery_fight --seed $s
done
echo done > exp/v14/IDENTITY-DONE
