#!/bin/sh
# supplementary: ring-first variant on single-dragon eval maps, seed 1, both sides (sequential, one slot)
mkdir -p runs/eval-ringfirst
for m in blobs_large_90030 portalrooms_large_90006 portals_large_90010 islands_medium_90000; do
  for side in 0 1; do
    d=runs/eval-ringfirst/$m-side$side
    if [ $side = 0 ]; then r=$(./play.sh variants/ringfirst opponent/bot maps/eval/sqheld_$m.map 1 $d); else r=$(./play.sh opponent/bot variants/ringfirst maps/eval/sqheld_$m.map 1 $d); fi
    case "$r" in "winner=$side "*) res=WIN;; *) res=loss;; esac
    echo "$m side$side $res | $r | $(python3 mytools/queenpath.py $d/game.replay $side | head -1 | sed 's/.*queen/queen/')"
  done
done
