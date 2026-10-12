#!/bin/zsh
# v1.1 with C2 (spec5): identity, chain and belief vs v1 and vs v1.1 without C2 (the same keys), the f-bin check with the guard table, the
# false-king split. Analysis only.
cd "$(dirname "$0")/../.."
X=exp/v11
A=$X/v11c-a-px4,$X/v11c-b-px4,$X/v11c-a2-px4,$X/v11c-b1-px4,$X/v11c-a3-px4
O=$X/v11-a-px4,$X/v11-b-px4,$X/v11-a2-px4,$X/v11-b1-px4,$X/v11-a3-px4
B=$X/v1-a-px4,$X/v1-b-px4,$X/v1-a2-px4,$X/v1-b1-px4,$X/v1-a3-px4
nice -n 10 node $X/identity.js $X/v1-fort $X/idoff2 > $X/identity2.txt 2>&1; echo "exit $?" >> $X/identity2.txt
nice -n 10 node exp/v1/local_report.js --a $A --b $B --names v1.1,v1 --jobs 3 --out $X/report-swarm-c.md > /dev/null 2> $X/report-swarm-c.err
nice -n 10 node exp/v1/local_report.js --a $A --b $O --names "v1.1 C2","v1.1 noC2" --jobs 3 --out $X/report-swarm-c2.md > /dev/null 2>> $X/report-swarm-c.err
nice -n 10 node exp/v1/local_report.js --a $X/v11c-fort --b $X/v1-fort --names v1.1,v1 --jobs 3 --out $X/report-fort-c.md > /dev/null 2>> $X/report-swarm-c.err
nice -n 10 node exp/v1/local_report.js --a $X/v11c-fort --b $X/v11-fort --names "v1.1 C2","v1.1 noC2" --jobs 3 --out $X/report-fort-c2.md > /dev/null 2>> $X/report-swarm-c.err
nice -n 10 node $X/fbin.js --sets v1.1=$A --sets v1=$B --jobs 3 --out $X/fbin-swarm-c.md 2> $X/fbin-swarm-c.err
nice -n 10 node $X/fbin.js --sets v1.1=$X/v11c-fort --sets v1=$X/v1-fort --maps all --jobs 3 --out $X/fbin-fort-c.md 2>> $X/fbin-swarm-c.err
nice -n 10 node $X/falseking.js $A --label "v1.1 C2 swarm" > $X/falseking-c.txt 2>&1
nice -n 10 node $X/falseking.js $X/v11c-fort --label "v1.1 C2 fort" >> $X/falseking-c.txt 2>&1
nice -n 10 node $X/sdflip.js $A --label "v1.1 C2" > $X/sdflip-c.txt 2>&1
echo done > $X/REPORT3-DONE
