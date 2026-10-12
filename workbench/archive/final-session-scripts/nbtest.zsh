#!/bin/zsh
# More seeds for the queen's no-blind-portal switch (builder's bot qbNB = one15 + QUEEN_NO_BLIND_PORTAL true) on the small
# portal maps: each of qbNB and mD15 against m3base, and qbNB against mD15, seeds 2-4, both seats.
cd ~/meow-redteam/solo || exit 1
diff <(grep "^constexpr" bots/mD15/main.cpp) <(grep "^constexpr" bots/qbNB/main.cpp) | head -6
cd ~/meow-redteam || exit 1
n=0
for mp in ladder_portals_1 ladder_stripes_1 gx_islands_24x12_911201; do
  m=$(ls maps/*/$mp.map | head -1)
  for s in 2 3 4; do
    for a in qbNB mD15; do
      [ -e solo/runs/nb_$a/$mp-seed$s-side0/result.txt ] || ./play.sh solo/bots/$a solo/bots/m3base $m $s solo/runs/nb_$a/$mp-seed$s-side0 > /dev/null 2>&1 &
      [ -e solo/runs/nb_$a/$mp-seed$s-side1/result.txt ] || ./play.sh solo/bots/m3base solo/bots/$a $m $s solo/runs/nb_$a/$mp-seed$s-side1 > /dev/null 2>&1 &
    done
    [ -e solo/runs/h2h_qbNB_v15/$mp-seed$s-side0/result.txt ] || ./play.sh solo/bots/qbNB solo/bots/mD15 $m $s solo/runs/h2h_qbNB_v15/$mp-seed$s-side0 > /dev/null 2>&1 &
    [ -e solo/runs/h2h_qbNB_v15/$mp-seed$s-side1/result.txt ] || ./play.sh solo/bots/mD15 solo/bots/qbNB $m $s solo/runs/h2h_qbNB_v15/$mp-seed$s-side1 > /dev/null 2>&1 &
    n=$((n+1)); [ $((n % 2)) -eq 0 ] && wait
  done
done
wait
echo "nb-done $(date '+%T')" >> solo/runs/run.log
