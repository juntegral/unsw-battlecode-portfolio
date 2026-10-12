#!/bin/bash
# usage: cmp.sh <botdir> <seeds> -> prints wins per opponent
cd "$(dirname "$0")"
B=$1; S=${2:-3}; tag=$(echo $B | tr '/' '_')
./batch.sh $B $S ../../bots/replay_rules_v8 ../../bots/archetype_hunter > /tmp/cmp_$tag.txt 2>&1
n=$(( S*10 ))
echo "$B v8=$(grep '^W' /tmp/cmp_$tag.txt | grep -c v8)/$n hunter=$(grep '^W' /tmp/cmp_$tag.txt | grep -c hunter)/$n"
