#!/bin/bash
# usage: batch.sh <botdir> <seeds> opp1 opp2 ...
cd "$(dirname "$0")"
B=$1; SEEDS=$2; shift 2
MAPS="autarky default devil portals prisoners_dilemma queen_of_spades schooltime slithery_fight trauma trophy"
for O in "$@"; do for M in $MAPS; do for s in $(seq ${SEED0:-1} $(( ${SEED0:-1} + SEEDS - 1 ))); do side=A; [ $((s%2)) = 0 ] && side=B; echo "$B $O $M $s $side"; done; done; done | xargs -P2 -L1 ./match.sh
