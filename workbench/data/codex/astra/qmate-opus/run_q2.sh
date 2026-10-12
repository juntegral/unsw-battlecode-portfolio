#!/bin/zsh
# qmate-opus: queue of on/off games (spec map:opp:seed), never more than two of mine running.
R=$HOME/meow-redteam
S=$R/solo
for d in $S/runs/qm_qm_*; do
  for l in $d/*.log(N); do
    [ -e ${l%.log}/result.txt ] || rm -rf $l ${l%.log}
  done
done
for spec in "$@"; do
  map=${spec%%:*}; rest=${spec#*:}; opp=${rest%%:*}; seed=${rest#*:}
  name=$(basename $map .map)
  for arm in qm_17 qm_on; do
    out=$S/runs/qm_${arm}_$opp/$name-seed$seed-side0
    [ -e $out.log ] && continue
    while [ $(pgrep -f "solo/runs/qm_qm_" | wc -l) -ge 2 ]; do sleep 3; done
    mkdir -p $S/runs/qm_${arm}_$opp
    $R/play.sh $S/bots/$arm $S/bots/$opp $R/$map $seed $out > $out.log 2>&1 &
    sleep 1
  done
done
wait
echo "$(date +%H:%M:%S) queue done"
