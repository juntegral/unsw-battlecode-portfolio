#!/bin/zsh
R=~/meow-redteam
for m in $@; do
  for b in mB19 mD18; do
    o=$R/solo/runs/rv19_$b/$m-seed1-side0
    mkdir -p $o
    $R/play.sh $R/solo/bots/$b $R/solo/bots/m3base $R/maps/un2/$m.map 1 $o > $o/stdout.txt 2>&1 &
  done
done
wait
date
for m in $@; do
  for b in mB19 mD18; do
    echo "$b $m $(cat $R/solo/runs/rv19_$b/$m-seed1-side0/result.txt)"
  done
done
