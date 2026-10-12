#!/bin/zsh
# sight-opus: 4 workers pull games from queue.txt (arm opp map seed side); no new game after $STOP (HHMM).
R=$HOME/meow-redteam
S=$R/solo
D=${0:A:h}
STOP=${STOP:-1407}
mkdir -p $D/claims
worker() {
  while read arm opp map seed side; do
    [ $(date +%H%M) -ge $STOP ] && break
    key=${arm}_${opp}_${map}_${seed}_${side}
    mkdir $D/claims/$key 2>/dev/null || continue
    dir=$S/runs/sg_${arm}_$opp
    out=$dir/ladder_$map-seed$seed-side$side
    mkdir -p $dir
    if [ $side = 0 ]; then
      $R/play.sh $S/bots/sg_$arm $S/bots/$opp $R/maps/ladder/ladder_$map.map $seed $out > $out.log 2>&1 &
    else
      $R/play.sh $S/bots/$opp $S/bots/sg_$arm $R/maps/ladder/ladder_$map.map $seed $out > $out.log 2>&1 &
    fi
    echo "$! $key" >> $D/pids.txt
    wait $!
    echo "$(date +%H:%M:%S) done $key" >> $D/pool.log
  done < $D/queue.txt
}
for k in 1 2 3 4; do worker & done
wait
echo "$(date +%H:%M:%S) pool finished" >> $D/pool.log
