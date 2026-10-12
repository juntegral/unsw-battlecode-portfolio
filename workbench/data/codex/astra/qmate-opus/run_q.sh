#!/bin/zsh
# qmate-opus: queue of on/off games, never more than four of mine running (counted by their out dir path).
R=$HOME/meow-redteam
S=$R/solo
SEED=${SEED:-7}
for spec in "$@"; do
  map=${spec%%:*}; opp=${spec#*:}
  name=$(basename $map .map)
  for arm in qm_17 qm_on; do
    out=$S/runs/qm_${arm}_$opp/$name-seed$SEED-side0
    [ -e $out ] && continue
    [ -e $out.log ] && continue
    while [ $(pgrep -f "solo/runs/qm_qm_" | wc -l) -ge 4 ]; do sleep 3; done
    mkdir -p $S/runs/qm_${arm}_$opp
    $R/play.sh $S/bots/$arm $S/bots/$opp $R/$map $SEED $out > $out.log 2>&1 &
    sleep 1
  done
done
wait
echo "$(date +%H:%M:%S) queue done"
