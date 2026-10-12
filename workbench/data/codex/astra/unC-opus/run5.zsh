#!/bin/zsh
# version bisect on the open 7x7, seat 0 against m3base; 2 workers; no new game after 14:10
R=$HOME/meow-redteam
w() {
  for b in $@; do
    [[ $(date +%H%M) -ge 1410 ]] && break
    o=$R/solo/runs/uc_t7_$b/uc_tiny7x7-seed1-side0
    [[ -e $o ]] && continue
    mkdir -p $o
    $R/play.sh $R/solo/bots/$b $R/solo/bots/m3base $R/maps/un2/uc_tiny7x7.map 1 $o > $R/solo/runs/uc_t7_$b/out.stdout 2>&1
  done
}
w mDone9 mDone7 mDone8 &
w mDone11 mDone10 &
wait
