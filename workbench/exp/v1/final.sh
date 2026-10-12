#!/bin/zsh
# v1 final build (coordinator 03:30): freeze bot/ -> versions/v1/bot, identity (fix off + FORT_W4 off: fortress s1, s2; + SWARM_AS_FORTRESS: 10 maps s1),
# CPU (3 games -v), the final local set (10 maps x 2 sides x proxy4_king, seed 1 = 20 games), then the reports and checks. At most 3 games at a time.
cd "$(dirname "$0")/../.."
X=exp/v1
okres() { while true; do m=$(memory_pressure | awk -F': ' '/free percentage/ {gsub("%","",$2); print $2}'); d=$(df -g . | awk 'NR==2 {print $4}'); if [ "${m:-100}" -ge 10 ] && [ "${d:-100}" -ge 20 ]; then return; fi; sleep 20; done; }
echo "$(date +%T) start" > $X/final.log
rm -rf $X/bot-v1post; mv versions/v1/bot $X/bot-v1post; cp -R bot versions/v1/bot; rm -rf versions/v1/bot/.unswbc-build
$X/make_variants.sh > $X/make_variants.out 2>&1
mkdir -p $X/identity3
okres
( nice -n 10 node tools/fingerprint.js --same benchmark $X/bot-fixoff --maps autarky,portals,prisoners_dilemma --seed 1 > $X/identity3/fixoff-fortress-s1.txt 2>&1; echo "exit $?" >> $X/identity3/fixoff-fortress-s1.txt
  nice -n 10 node tools/fingerprint.js --same benchmark $X/bot-fixoff-swf --maps autarky,portals,prisoners_dilemma,queen_of_spades,trophy --seed 1 > $X/identity3/swf-s1-part2.txt 2>&1; echo "exit $?" >> $X/identity3/swf-s1-part2.txt ) &
( nice -n 10 node tools/fingerprint.js --same benchmark $X/bot-fixoff --maps autarky,portals,prisoners_dilemma --seed 2 > $X/identity3/fixoff-fortress-s2.txt 2>&1; echo "exit $?" >> $X/identity3/fixoff-fortress-s2.txt ) &
( nice -n 10 node tools/fingerprint.js --same benchmark $X/bot-fixoff-swf --maps slithery_fight,trauma,schooltime,default,devil --seed 1 > $X/identity3/swf-s1-part1.txt 2>&1; echo "exit $?" >> $X/identity3/swf-s1-part1.txt ) &
wait
echo "$(date +%T) identity done" >> $X/final.log
mkdir -p $X/cpu-final
cpu() { local m=$1; local tag=$2; (cd $X/cpu-final && nice -n 10 ../../../tools/unswbc run ../../../$m ../../../versions/v1/bot ../../../bots/proxy4_swarm --sandbox --seed 1 --no-logs --no-draw -o $tag.replay -v 2>&1 | grep -i "points per turn\|error\|timed out" > $tag.txt; rm -f $tag.replay); }
okres
cpu maps/online-20260927/schooltime.map schooltime-a &
cpu maps/server-b/slithery_fight_b.map slithery_fight-b &
cpu maps/online-20260927/default.map default-a &
wait
echo "$(date +%T) cpu done" >> $X/final.log
okres
nice -n 10 node tools/eval.js --bot versions/v1/bot --label v1final-a-px4 --out $X/v1final-a-px4 --opps proxy4_king --seeds 1 --maps maps/online-20260927 --jobs 3 > $X/eval-v1final-a.log 2>&1
echo "$(date +%T) final set done" >> $X/final.log
nice -n 10 node $X/local_report.js --a $X/v1final-a-px4 --b $X/v0t-a-px4 --names v1final,v0t --jobs 3 --out $X/report-final-vs-v0.md > /dev/null 2> $X/report-final.err
nice -n 10 node $X/local_report.js --a $X/v1final-a-px4 --b $X/v1-a-px4 --names v1final,v1pre --jobs 3 --out $X/report-final-vs-pre.md > /dev/null 2> $X/report-final-pre.err
nice -n 10 node $X/spatial.js $X/v1final-a-px4 --label "v1 final (a, proxy4_king, 20 games)" > $X/spatial-final.md 2>&1
nice -n 10 node $X/spatial.js $X/v0t-a-px4 --opp proxy4_king --label "v0 tagged (a, proxy4_king, same 20 keys)" > $X/spatial-v0t.md 2>&1
nice -n 10 node $X/spatial.js $X/v1-a-px4 --opp proxy4_king --label "v1 pre-cleanup (a, proxy4_king, same 20 keys)" > $X/spatial-v1pre.md 2>&1
nice -n 10 node $X/fivebcheck.js $X/v1final-a-px4 $X/v0t-a-px4 $X/v1-a-px4 > $X/fiveb-check.txt 2>&1
node $X/mock_online.js $X/v1final-a-px4 $X/mock local-v1final-a-px4 > /dev/null
nice -n 10 node eval/system_report.js local-v1final-a-px4 --vs local-v0t-a-px4 --name "v1 final local (proxy4_king, a, 20 games)" --vs-name "v0 tagged local (proxy4, a)" --online $X/mock --no-extract --out $X/system-report-local-final.md > /dev/null 2> $X/system-report-local-final.err
echo "$(date +%T) all done" >> $X/final.log
echo done > $X/FINAL-DONE
