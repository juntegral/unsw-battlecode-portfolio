#!/bin/zsh
# until.zsh <seconds> : return after that many seconds, or earlier when one of my pair batches writes a new done line.
L=~/meow-redteam/solo/runs/run.log
N0=$(grep -c "qda-done\|noram-done\|cmax-done" $L)
END=$(( $(date +%s) + $1 ))
while [ $(date +%s) -lt $END ]; do
  [ "$(grep -c 'qda-done\|noram-done\|cmax-done' $L)" -gt "$N0" ] && break
  sleep 15
done
date "+%H:%M:%S"; tail -n 3 $L | cut -c1-80
