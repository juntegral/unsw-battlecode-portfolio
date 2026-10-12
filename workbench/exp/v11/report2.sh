#!/bin/zsh
# v1.1 local reports over both seed batches (spec1 + spec2: 112 paired swarm games), after exp/v11/runq.js spec2.json. Analysis only.
cd "$(dirname "$0")/../.."
X=exp/v11
A=$X/v11-a-px4,$X/v11-b-px4,$X/v11-a2-px4,$X/v11-b1-px4,$X/v11-a3-px4
B=$X/v1-a-px4,$X/v1-b-px4,$X/v1-a2-px4,$X/v1-b1-px4,$X/v1-a3-px4
nice -n 10 node exp/v1/local_report.js --a $A --b $B --names v1.1,v1 --jobs 3 --out $X/report-swarm-all.md > /dev/null 2> $X/report-swarm-all.err
nice -n 10 node $X/fbin.js --sets v1.1=$A --sets v1=$B --jobs 3 --out $X/fbin-swarm-all.md 2> $X/fbin-swarm-all.err
nice -n 10 node $X/fbin.js --sets v1.1=$A --sets v1=$B --opp proxy4_king --jobs 3 --out $X/fbin-swarm-all-king.md 2>> $X/fbin-swarm-all.err
nice -n 10 node $X/fbin.js --sets v1.1=$A --sets v1=$B --opp proxy4_swarm --jobs 3 --out $X/fbin-swarm-all-swarm.md 2>> $X/fbin-swarm-all.err
nice -n 10 node $X/sdflip.js $A --label v1.1 > $X/sdflip-all.txt 2>&1
nice -n 10 node $X/sdflip.js $B --label v1 >> $X/sdflip-all.txt 2>&1
nice -n 10 node $X/falseking.js $A --label v1.1-swarm > $X/falseking-all.txt 2>&1
nice -n 10 node $X/falseking.js $B --label v1-swarm >> $X/falseking-all.txt 2>&1
nice -n 10 node $X/falseking.js $X/v11-fort --label v1.1-fort >> $X/falseking-all.txt 2>&1
nice -n 10 node $X/falseking.js $X/v1-fort --label v1-fort >> $X/falseking-all.txt 2>&1
nice -n 10 node exp/v1/spatial.js $A --label "v1.1 (112 swarm games)" > $X/spatial-v11-all.md 2>&1
nice -n 10 node exp/v1/spatial.js $B --label "v1 (same keys)" > $X/spatial-v1-all.md 2>&1
echo done > $X/REPORT2-DONE
