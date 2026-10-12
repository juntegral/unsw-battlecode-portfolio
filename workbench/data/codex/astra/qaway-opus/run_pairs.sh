#!/bin/zsh
# qaway-opus: arms $ARMS against $OPP, same map, seed and side; one spec (all arms) at a time.
R=$HOME/meow-redteam
S=$R/solo
OPP=${OPP:-mD15}
ARMS=(${=ARMS:-qa_L qa_5 qa_7})
for spec in "$@"; do
  map=${spec%%:*}; rest=${spec#*:}; seed=${rest%%:*}; side=${rest#*:}
  name=$(basename $map .map)
  for arm in $ARMS; do
    dir=$S/runs/${arm}_$OPP
    out=$dir/$name-seed$seed-side$side
    [ -e $out ] && continue
    mkdir -p $dir
    log=$dir/$name-seed$seed-side$side.log
    if [ $side = 0 ]; then
      $R/play.sh $S/bots/$arm $S/bots/$OPP $R/$map $seed $out > $log 2>&1 &
    else
      $R/play.sh $S/bots/$OPP $S/bots/$arm $R/$map $seed $out > $log 2>&1 &
    fi
  done
  wait
  echo "$(date +%H:%M:%S) done $OPP $name seed$seed side$side"
done
