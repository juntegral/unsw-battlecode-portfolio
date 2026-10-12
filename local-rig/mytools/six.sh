#!/bin/sh
# six.sh <variant> <tag> [maps...] : play variant on the given dev maps, both sides, seed 1
v=$1; tag=$2; shift 2
for m in "$@"; do
  ./play.sh variants/$v opponent/bot maps/dev/sqheld_$m.map 1 runs/$tag-$m-0 | sed "s/^/$m side0 (win=0): /"
  ./play.sh opponent/bot variants/$v maps/dev/sqheld_$m.map 1 runs/$tag-$m-1 | sed "s/^/$m side1 (win=1): /"
done
