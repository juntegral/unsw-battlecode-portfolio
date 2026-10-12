#!/bin/zsh
# v1.1 CPU per turn (as exp/v1/final.sh's cpu(): the three heaviest swarm games vs proxy4_swarm, unswbc -v "points per turn") and the upload's local
# smoke test (exp/v1/smoke_upload.js: tools/submit.js's two sandbox games, no network). Waits until fewer than 4 games run machine-wide, then runs
# at most 3 at a time.
cd "$(dirname "$0")/../.."
X=exp/v11
mkdir -p $X/cpu
waitcap() { while [ "$(pgrep -f 'unswbc-clean.py run' | wc -l)" -ge "$1" ]; do sleep 5; done; }
cpu() { local m=$1; local tag=$2; (cd $X/cpu && nice -n 10 ../../../tools/unswbc run ../../../$m ../../../versions/v1.1/bot ../../../bots/proxy4_swarm --sandbox --seed 1 --no-logs --no-draw -o $tag.replay -v 2>&1 | grep -i "points per turn\|error\|timed out" > $tag.txt; rm -f $tag.replay); }
waitcap 4; cpu maps/online-20260927/schooltime.map schooltime-a &
sleep 3; waitcap 5; cpu maps/server-b/slithery_fight_b.map slithery_fight-b &
sleep 3; waitcap 6; cpu maps/online-20260927/default.map default-a &
wait
waitcap 5
nice -n 10 node exp/v1/smoke_upload.js versions/v1.1/bot > $X/smoke-upload.txt 2>&1; echo "exit $?" >> $X/smoke-upload.txt
echo done > $X/CPU-DONE
