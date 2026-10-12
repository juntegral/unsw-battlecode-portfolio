#!/bin/bash
# usage: why.sh <map> <opp> <seed> [n]
cd "$(dirname "$0")"
../_tools/unswbc run ../../maps/online-20260927/$1.map ${5:-bot} $2 --sandbox --seed $3 -v > /tmp/g1v.txt 2>&1
grep "died\|wins\|points per" /tmp/g1v.txt
grep "(team A) died" /tmp/g1v.txt | while read -r a r b id rest; do r=${r%:}; echo "== bot $id R$r $rest"; for k in $(seq $((r-${4:-3})) $r); do grep -A1 "round $k: bot $id (team A) stdout" /tmp/g1v.txt | grep LOG | cut -c1-330; done; done
