#!/bin/zsh
R=~/meow-redteam
L="~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/review19-opus"
for m in $@; do
  for b in mB19 mD18; do
    o=$R/solo/runs/rv19_$b/$m-seed1-side0
    mkdir -p $o
    rm -f $o/stdout.txt
    $R/play.sh $R/solo/bots/$b $R/solo/bots/m3base $R/maps/un2/$m.map 1 $o > $L/$b-$m.log 2>&1 &
  done
done
wait
date
for m in $@; do
  for b in mB19 mD18; do
    echo "$b $m $(cat $R/solo/runs/rv19_$b/$m-seed1-side0/result.txt)"
  done
done
