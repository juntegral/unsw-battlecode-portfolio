#!/bin/zsh
# third worker: older builds and arms on the open 7x7, seat 0 against m3base
R=$HOME/meow-redteam
for b in mD16 mDone13 mDone5 uc_nqh uc_nqb mD15; do
  [[ $(date +%H%M) -ge 1410 ]] && break
  o=$R/solo/runs/uc_t7_$b/uc_tiny7x7-seed1-side0
  [[ -e $o ]] && continue
  mkdir -p $o
  $R/play.sh $R/solo/bots/$b $R/solo/bots/m3base $R/maps/un2/uc_tiny7x7.map 1 $o > $R/solo/runs/uc_t7_$b/out.stdout 2>&1
done
