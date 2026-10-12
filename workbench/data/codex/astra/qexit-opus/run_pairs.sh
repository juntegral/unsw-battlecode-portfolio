#!/bin/zsh
# qexit-opus: on (qx_one4) and off (qx_base) against mNps, same map, seed and side; two games at a time.
R=$HOME/meow-redteam
S=$R/solo
ON=${ON:-qx_one4}
for spec in "$@"; do
  map=${spec%%:*}; rest=${spec#*:}; seed=${rest%%:*}; side=${rest#*:}
  name=$(basename $map .map)
  for arm in qx_base $ON; do
    out=$S/runs/${arm}_r/$name-seed$seed-side$side
    [ -e $out ] && continue
    mkdir -p $S/runs/${arm}_r
    log=$S/runs/${arm}_r/$name-seed$seed-side$side.log
    if [ $side = 0 ]; then
      $R/play.sh $S/bots/$arm $S/bots/mNps $R/$map $seed $out > $log 2>&1 &
    else
      $R/play.sh $S/bots/mNps $S/bots/$arm $R/$map $seed $out > $log 2>&1 &
    fi
  done
  wait
  echo "$(date +%H:%M:%S) done $name seed$seed side$side"
done
