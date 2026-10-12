#!/bin/zsh
# after exp/v1/run_local.sh (pre-cleanup v1 and v0t, 60 games per layout): swap in the post-cleanup build (coordinator 03:09/03:20: one swarm
# split policy, one conversion rule, nearest-first sd), re-check identity, CPU on the final build, the post-cleanup local set (7 swarm maps x
# 2 sides x proxy4_king, proxy4_elim: 28 games per layout), then the reports. At most 3 games at a time.
cd "$(dirname "$0")/../.."
X=exp/v1
okres() { while true; do m=$(memory_pressure | awk -F': ' '/free percentage/ {gsub("%","",$2); print $2}'); d=$(df -g . | awk 'NR==2 {print $4}'); if [ "${m:-100}" -ge 10 ] && [ "${d:-100}" -ge 20 ]; then return; fi; echo "$(date +%T) pause mem ${m}% disk ${d}G" >> $X/pause.log; sleep 20; done; }
while [ ! -f $X/LOCAL-DONE ]; do sleep 10; done
echo "$(date +%T) local done" >> $X/finish2.log
# freeze: the pre-cleanup build that played the 240 games -> exp/v1/bot-v1pre; the post-cleanup bot/ -> versions/v1/bot
rm -rf $X/bot-v1pre; mv versions/v1/bot $X/bot-v1pre; cp -R bot versions/v1/bot; rm -rf versions/v1/bot/.unswbc-build
$X/make_variants.sh > /dev/null
# pre-cleanup reports (analysis only, nice) in the background
( nice -n 10 node $X/local_report.js --a $X/v1-a-px4 --b $X/v0t-a-px4 --names v1pre,v0t --jobs 2 --out $X/report-a.md > /dev/null 2> $X/report-a.err
  nice -n 10 node $X/local_report.js --a $X/v1-b-px4 --b $X/v0t-b-px4 --names v1pre,v0t --jobs 2 --out $X/report-b.md > /dev/null 2> $X/report-b.err
  nice -n 10 node $X/local_report.js --a $X/v1-a-px4,$X/v1-b-px4 --b $X/v0t-a-px4,$X/v0t-b-px4 --names v1pre,v0t --jobs 2 --out $X/report-ab.md > /dev/null 2> $X/report-ab.err
  echo done > $X/REPORT-PRE-DONE ) &
# identity (post-cleanup build, fix off)
mkdir -p $X/identity2
okres
( nice -n 10 node tools/fingerprint.js --same benchmark $X/bot-fixoff --maps autarky,portals,prisoners_dilemma --seed 1 > $X/identity2/fixoff-fortress-s1.txt 2>&1; echo "exit $?" >> $X/identity2/fixoff-fortress-s1.txt
  nice -n 10 node tools/fingerprint.js --same benchmark $X/bot-fixoff-swf --maps autarky,portals,prisoners_dilemma,queen_of_spades,trophy --seed 1 > $X/identity2/swf-s1-part2.txt 2>&1; echo "exit $?" >> $X/identity2/swf-s1-part2.txt ) &
( nice -n 10 node tools/fingerprint.js --same benchmark $X/bot-fixoff --maps autarky,portals,prisoners_dilemma --seed 2 > $X/identity2/fixoff-fortress-s2.txt 2>&1; echo "exit $?" >> $X/identity2/fixoff-fortress-s2.txt ) &
( nice -n 10 node tools/fingerprint.js --same benchmark $X/bot-fixoff-swf --maps slithery_fight,trauma,schooltime,default,devil --seed 1 > $X/identity2/swf-s1-part1.txt 2>&1; echo "exit $?" >> $X/identity2/swf-s1-part1.txt ) &
wait
echo "$(date +%T) identity done" >> $X/finish2.log
# CPU on the final build (3 games)
mkdir -p $X/cpu
cpu() { local m=$1; local tag=$2; (cd $X/cpu && nice -n 10 ../../../tools/unswbc run ../../../$m ../../../versions/v1/bot ../../../bots/proxy4_swarm --sandbox --seed 1 --no-logs --no-draw -o $tag.replay -v 2>&1 | grep -i "points per turn\|error\|timed out" > $tag.txt; rm -f $tag.replay); }
okres
cpu maps/online-20260927/schooltime.map schooltime-a &
cpu maps/server-b/slithery_fight_b.map slithery_fight-b &
cpu maps/online-20260927/default.map default-a &
wait
echo "$(date +%T) cpu done" >> $X/finish2.log
# post-cleanup local set
okres
nice -n 10 node tools/eval.js --bot versions/v1/bot --label v1post-a-px4 --out $X/v1post-a-px4 --opps proxy4_king,proxy4_elim --seeds 1 --maps $X/maps-swarm-a --jobs 3 > $X/eval-v1post-a.log 2>&1
okres
nice -n 10 node tools/eval.js --bot versions/v1/bot --label v1post-b-px4 --out $X/v1post-b-px4 --opps proxy4_king,proxy4_elim --seeds 2 --maps $X/maps-swarm-b --jobs 3 > $X/eval-v1post-b.log 2>&1
echo "$(date +%T) post evals done" >> $X/finish2.log
while [ ! -f $X/REPORT-PRE-DONE ]; do sleep 5; done
nice -n 10 node $X/local_report.js --a $X/v1post-a-px4,$X/v1post-b-px4 --b $X/v1-a-px4,$X/v1-b-px4 --names v1post,v1pre --jobs 3 --out $X/report-post-vs-pre.md > /dev/null 2> $X/report-post-vs-pre.err
nice -n 10 node $X/local_report.js --a $X/v1post-a-px4,$X/v1post-b-px4 --b $X/v0t-a-px4,$X/v0t-b-px4 --names v1post,v0t --jobs 3 --out $X/report-post-vs-v0.md > /dev/null 2> $X/report-post-vs-v0.err
for s in v1-a-px4 v1-b-px4 v0t-a-px4 v0t-b-px4 v1post-a-px4 v1post-b-px4; do node $X/mock_online.js $X/$s $X/mock local-$s > /dev/null; done
nice -n 10 node eval/system_report.js local-v1-a-px4+local-v1-b-px4 --vs local-v0t-a-px4+local-v0t-b-px4 --name "v1 pre-cleanup local (proxy4, a+b, 120 games)" --vs-name "v0 tagged local (proxy4, a+b, 120 games)" --online $X/mock --no-extract --out $X/system-report-local-pre.md > /dev/null 2> $X/system-report-local-pre.err
nice -n 10 node eval/system_report.js local-v1post-a-px4+local-v1post-b-px4 --vs local-v0t-a-px4+local-v0t-b-px4 --name "v1 local (proxy4, swarm maps, a+b, 56 games)" --vs-name "v0 tagged local (proxy4, a+b)" --online $X/mock --no-extract --out $X/system-report-local-post.md > /dev/null 2> $X/system-report-local-post.err
echo "$(date +%T) all done" >> $X/finish2.log
echo done > $X/FINISH2-DONE
