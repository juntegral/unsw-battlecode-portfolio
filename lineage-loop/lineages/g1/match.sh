#!/bin/bash
# usage: match.sh <botdir> <opp> <map> <seed> <side A|B>
cd "$(dirname "$0")"
B=$1; O=$2; M=$3; S=$4; SIDE=$5
MP=../../maps/online-20260927/$M.map
[ -f "$MP" ] || MP=maps/$M.map
if [ "$SIDE" = A ]; then out=$(../_tools/unswbc run $MP $B $O --sandbox --seed $S 2>&1); else out=$(../_tools/unswbc run $MP $O $B --sandbox --seed $S 2>&1); fi
res=$(echo "$out" | grep -E "wins|draw" | tail -1)
w=$(echo "$res" | grep -oE "team [AB] wins" | cut -c6)
if [ -z "$w" ]; then r=D; elif [ "$w" = "$SIDE" ]; then r=W; else r=L; fi
echo "$r $M $(basename $O) seed$S side$SIDE :: $res"
