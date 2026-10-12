#!/bin/zsh
# v1.1 local reports (versions/v1.1/VERSION.md §3), after exp/v11/runq.js spec1.json: identity, chain and belief (exp/v1/local_report.js), the f-bin
# spatial check (exp/v11/fbin.js), the x-band check (exp/v1/spatial.js). Analysis only (no games).
cd "$(dirname "$0")/../.."
X=exp/v11
nice -n 10 node $X/identity.js $X/v1-fort $X/idoff > $X/identity.txt 2>&1; echo "exit $?" >> $X/identity.txt
nice -n 10 node exp/v1/local_report.js --a $X/v11-a-px4,$X/v11-b-px4 --b $X/v1-a-px4,$X/v1-b-px4 --names v1.1,v1 --jobs 3 --out $X/report-swarm.md > /dev/null 2> $X/report-swarm.err
nice -n 10 node exp/v1/local_report.js --a $X/v11-fort --b $X/v1-fort --names v1.1,v1 --jobs 3 --out $X/report-fort.md > /dev/null 2> $X/report-fort.err
nice -n 10 node $X/fbin.js --sets v1.1=$X/v11-a-px4,$X/v11-b-px4 --sets v1=$X/v1-a-px4,$X/v1-b-px4 --jobs 3 --out $X/fbin-swarm.md 2> $X/fbin-swarm.err
nice -n 10 node $X/fbin.js --sets v1.1=$X/v11-a-px4,$X/v11-b-px4 --sets v1=$X/v1-a-px4,$X/v1-b-px4 --opp proxy4_king --jobs 3 --out $X/fbin-swarm-king.md 2>> $X/fbin-swarm.err
nice -n 10 node $X/fbin.js --sets v1.1=$X/v11-a-px4,$X/v11-b-px4 --sets v1=$X/v1-a-px4,$X/v1-b-px4 --opp proxy4_swarm --jobs 3 --out $X/fbin-swarm-swarm.md 2>> $X/fbin-swarm.err
nice -n 10 node exp/v1/spatial.js $X/v11-a-px4,$X/v11-b-px4 --label "v1.1 (swarm a s1 + b s2, proxy4_king + proxy4_swarm)" > $X/spatial-v11.md 2>&1
nice -n 10 node exp/v1/spatial.js $X/v1-a-px4,$X/v1-b-px4 --label "v1 (same keys)" > $X/spatial-v1.md 2>&1
echo done > $X/REPORT-DONE
