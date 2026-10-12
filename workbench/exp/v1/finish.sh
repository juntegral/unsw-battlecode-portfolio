#!/bin/zsh
# after exp/v1/run_local.sh: CPU check (3 games with -v on the heaviest swarm maps, v1 vs proxy4_swarm), the local reports, the mock
# online sets and eval/system_report.js on them.
cd "$(dirname "$0")/../.."
X=exp/v1
while [ ! -f $X/LOCAL-DONE ]; do sleep 10; done
mkdir -p $X/cpu
cpu() { local m=$1; local tag=$2; (cd $X/cpu && nice -n 10 ../../../tools/unswbc run ../../../$m ../../../versions/v1/bot ../../../bots/proxy4_swarm --sandbox --seed 1 --no-logs --no-draw -o $tag.replay -v 2>&1 | grep -i "points per turn\|error\|timed out" > $tag.txt); }
cpu maps/online-20260927/schooltime.map schooltime-a &
cpu maps/server-b/slithery_fight_b.map slithery_fight-b &
cpu maps/online-20260927/default.map default-a &
wait
rm -f $X/cpu/*.replay
nice -n 10 node $X/local_report.js --a $X/v1-a-px4 --b $X/v0t-a-px4 --names v1,v0t --jobs 3 --out $X/report-a.md > /dev/null 2> $X/report-a.err
nice -n 10 node $X/local_report.js --a $X/v1-b-px4 --b $X/v0t-b-px4 --names v1,v0t --jobs 3 --out $X/report-b.md > /dev/null 2> $X/report-b.err
nice -n 10 node $X/local_report.js --a $X/v1-a-px4,$X/v1-b-px4 --b $X/v0t-a-px4,$X/v0t-b-px4 --names v1,v0t --jobs 3 --out $X/report-ab.md > /dev/null 2> $X/report-ab.err
for s in v1-a-px4 v1-b-px4 v0t-a-px4 v0t-b-px4; do node $X/mock_online.js $X/$s $X/mock local-$s; done
nice -n 10 node eval/system_report.js local-v1-a-px4+local-v1-b-px4 --vs local-v0t-a-px4+local-v0t-b-px4 --name "v1 local (proxy4, a+b)" --vs-name "v0 tagged local (proxy4, a+b)" --online $X/mock --no-extract --out $X/system-report-local.md > /dev/null 2> $X/system-report-local.err
echo done > $X/FINISH-DONE
