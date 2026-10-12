#!/bin/zsh
# qmate-opus: on (qm_on) and off (qm_17) against mD17 and m3base, same map and seed, side 0; four games at a time.
R=$HOME/meow-redteam
S=$R/solo
SEED=${SEED:-7}
for map in "$@"; do
  name=$(basename $map .map)
  for opp in mD17 m3base; do
    for arm in qm_17 qm_on; do
      out=$S/runs/qm_${arm}_$opp/$name-seed$SEED-side0
      [ -e $out ] && continue
      mkdir -p $S/runs/qm_${arm}_$opp
      $R/play.sh $S/bots/$arm $S/bots/$opp $R/$map $SEED $out > $out.log 2>&1 &
    done
  done
  wait
  echo "$(date +%H:%M:%S) done $name"
done
