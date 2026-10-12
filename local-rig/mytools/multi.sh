#!/bin/sh
# multi.sh <variant> <tag> "<seeds>" maps... : variant vs opponent, both sides; prints wins per map/side
v=$1; tag=$2; seeds=$3; shift 3
tot=0; win=0
for m in "$@"; do
  for side in 0 1; do
    w=0; n=0; ends=""
    for s in $seeds; do
      out=runs/$tag/$m-s$s-side$side
      mkdir -p runs/$tag
      if [ $side = 0 ]; then r=$(./play.sh variants/$v opponent/bot maps/dev/sqheld_$m.map $s $out); else r=$(./play.sh opponent/bot variants/$v maps/dev/sqheld_$m.map $s $out); fi
      n=$((n+1)); case "$r" in "winner=$side "*) w=$((w+1));; esac
      rd=$(echo "$r" | sed -E 's/.*how=([a-z_]+).*rounds=([0-9]+).*/\1:\2/')
      ends="$ends $rd"
    done
    echo "$tag $m side$side: $w/$n  [$ends ]"
    tot=$((tot+n)); win=$((win+w))
  done
done
echo "$tag TOTAL $win/$tot"
