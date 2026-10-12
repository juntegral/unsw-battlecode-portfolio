#!/bin/zsh
# v1.1 CPU per turn (the three heaviest swarm games vs proxy4_swarm, unswbc -v) and the upload's local smoke test (exp/v1/smoke_upload.js) for one
# bot dir. At most 3 games of ours at a time, and none while 6 run machine-wide; nothing below 21 GB free.
# usage: exp/v11/cpu2.sh <bot dir> <tag>
cd "$(dirname "$0")/../.."
X=exp/v11; B=$1; T=$2
mkdir -p $X/cpu-$T
waitcap() { while [ "$(pgrep -f 'unswbc-clean.py run' | wc -l)" -ge "$1" ]; do sleep 5; done; }
diskok() { [ "$(df -g / | awk 'NR==2 {print $4}')" -ge 21 ]; }
cpu() { local m=$1; local tag=$2; (cd $X/cpu-$T && nice -n 10 ../../../tools/unswbc run ../../../$m ../../../$B ../../../bots/proxy4_swarm --sandbox --seed 1 --no-logs --no-draw -o $tag.replay -v 2>&1 | grep -i "points per turn\|error\|timed out" > $tag.txt; rm -f $tag.replay); }
diskok || { echo "disk below 21 GB" > $X/cpu-$T/STOP; exit 1; }
waitcap 4; cpu maps/online-20260927/schooltime.map schooltime-a &
sleep 3; waitcap 5; cpu maps/server-b/slithery_fight_b.map slithery_fight-b &
sleep 3; waitcap 6; cpu maps/online-20260927/default.map default-a &
wait
waitcap 5
nice -n 10 node exp/v1/smoke_upload.js $B > $X/smoke-upload-$T.txt 2>&1; echo "exit $?" >> $X/smoke-upload-$T.txt
