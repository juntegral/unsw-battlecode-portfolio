#!/bin/sh
# pair.sh <variant> <tag> <seed> maps... : both sides of each map run in parallel (2 slots), prints result + queen status
v=$1; tag=$2; seed=$3; shift 3
mkdir -p runs/$tag
for m in "$@"; do
  ./play.sh variants/$v opponent/bot maps/dev/sqheld_$m.map $seed runs/$tag/$m-s$seed-side0 > runs/$tag/$m-s$seed-side0.txt 2>&1 &
  ./play.sh opponent/bot variants/$v maps/dev/sqheld_$m.map $seed runs/$tag/$m-s$seed-side1 > runs/$tag/$m-s$seed-side1.txt 2>&1 &
  wait
  for side in 0 1; do
    d=runs/$tag/$m-s$seed-side$side
    r=$(cat $d.txt)
    case "$r" in "winner=$side "*) res=WIN;; *) res=loss;; esac
    q=$(grep -E "dragon $side," $d/engine.log | sed -E 's/round ([0-9]+).*: (.*)/queen died r\1 \2/')
    oq=$(grep -E "dragon $((1-side))," $d/engine.log | sed -E 's/round ([0-9]+).*: (.*)/their queen died r\1/')
    echo "$tag $m side$side $res | $r | ${q:-queen ALIVE} | ${oq:-their queen alive}"
  done
done
