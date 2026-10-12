#!/bin/zsh
# v1.3 HV report: the pocket economy (exp/v13/pocketnet.js), the chain and safety (exp/v1/local_report.js) and the outcome table (exp/v11/fbin.js),
# HV build vs v1.2 on the same keys (Trauma, Slithery a/b x both sides x proxy4_king/proxy4_swarm x seeds 1-2). Analysis only.
cd "$(dirname "$0")/../.."
X=exp/v13
H=$X/hv-a,$X/hv-b
B=exp/v11/v11bc-a-px4,exp/v11/v11bc-b-px4,$X/base-a,$X/base-b
nice -n 10 node $X/pocketnet.js --sets v1.3-HV=$H --sets v1.2=$B --out $X/pocketnet-hv.md > /dev/null 2> $X/pocketnet-hv.err
nice -n 10 node exp/v1/local_report.js --a $H --b $B --names v1.3-HV,v1.2 --jobs 3 --out $X/report-hv.md > /dev/null 2> $X/report-hv.err
nice -n 10 node exp/v11/fbin.js --sets v1.3-HV=$H --sets v1.2=$B --jobs 3 --out $X/fbin-hv.md 2> $X/fbin-hv.err
echo done > $X/REPORT-HV-DONE
