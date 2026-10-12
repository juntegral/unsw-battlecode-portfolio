#!/bin/zsh
# run_arms.sh <seed> <arm>... : each arm plays the red-team bot on every map above 1200 cells, both sides. Two games at a time.
cd ~/meow-redteam || exit 1
SEED=$1; shift
MAPS=(maps/dev/sqheld_blobs_large_90009.map maps/dev/sqheld_portalrooms_large_90013.map maps/dev/sqheld_stripes_large_90002.map maps/eval/sqheld_open_large_90036.map maps/eval/sqheld_blobs_large_90030.map maps/eval/sqheld_portalrooms_large_90003.map maps/eval/sqheld_portalrooms_large_90006.map maps/eval/sqheld_portals_large_90010.map maps/eval/sqheld_rooms_large_90035.map)
[ -n "$SOLO_MAPS" ] && MAPS=(${=SOLO_MAPS})
OPP=${SOLO_OPP:-bot}
jobs_file=$(mktemp)
for M in $MAPS; do
  N=${${M:t}%.map}
  for ARM in "$@"; do
    for SIDE in 0 1; do
      OUT=solo/runs/$ARM/$N-seed$SEED-side$SIDE
      [ -e $OUT/game.replay ] && continue
      rm -rf $OUT
      if [ $SIDE = 0 ]; then echo "./play.sh solo/bots/$ARM $OPP $M $SEED $OUT" >> $jobs_file
      else echo "./play.sh $OPP solo/bots/$ARM $M $SEED $OUT" >> $jobs_file; fi
    done
  done
done
wc -l < $jobs_file
xargs -P 2 -I{} sh -c '{} >> solo/runs/run.log 2>&1' < $jobs_file
echo "done $(date '+%F %T')" >> solo/runs/run.log
