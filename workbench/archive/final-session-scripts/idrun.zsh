#!/bin/zsh
# Identity check: main's bot and the all-off solo source on six maps, both sides, against m3base.
cd ~/meow-redteam || exit 1
rm -rf solo/runs/id_mSolo solo/runs/id_mMain
for n in sqheld_blobs_small_90028 sqheld_portals_small_90029 sqheld_open_small_90012 ladder_stripes_1 ladder_tower_defense_1 sqheld_open_medium_90017; do
  m=$(ls maps/*/$n.map | head -1)
  for a in mSolo mMain; do
    ./play.sh solo/bots/$a solo/bots/m3base $m 1 solo/runs/id_$a/$n-seed1-side0 > /dev/null 2>&1 &
    ./play.sh solo/bots/m3base solo/bots/$a $m 1 solo/runs/id_$a/$n-seed1-side1 > /dev/null 2>&1 &
  done
  wait
done
for d in solo/runs/id_mSolo/*/; do
  n=$(basename $d); a=$d/game.replay; b=solo/runs/id_mMain/$n/game.replay
  echo "$n size $(wc -c < $a | tr -d ' ')/$(wc -c < $b | tr -d ' ') differing bytes $(cmp -l $a $b 2>/dev/null | wc -l | tr -d ' ') | $(cat $d/result.txt | tr '\n' ' ' | cut -c1-48)"
done
