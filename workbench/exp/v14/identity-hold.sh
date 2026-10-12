#!/bin/zsh
# v1.4 §7 check: the hold switches off (versions/v1.4/bot now) against the measured v1.4 (commit 76b3879), the scripted a-layout maps, seeds 1-2
cd "$(dirname "$0")/../.."
for s in 1 2; do
  [ "$(df -g / | awk 'NR==2 {print $4}')" -ge 21 ] || { echo "disk < 21 GB: stop"; exit 1; }
  nice -n 10 node tools/fingerprint.js --same /private/tmp/claude-501/-Users-jun-01--Project---------unsw-arena/ab529c8b-1bec-404e-b9b6-2b23c283b013/scratchpad/v14-76b3879/versions/v1.4/bot versions/v1.4/bot --maps devil,trophy,schooltime,slithery_fight,default --seed $s
done
echo done > exp/v14/IDENTITY-HOLD-DONE
