#!/bin/zsh
# Add the finished one15 sets to the label cache and print pearls by r100 per map for one11, one14, one15.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
R=data/analysis/ladder/dossier/online/label_report.py
A=()
for l in c1 p1 s1 q1; do [ -f data/online/smoke/one15-$l-result.txt ] && A+=(one15-$l:old); done
[ ${#A} -eq 0 ] && exit 0
REFS=()
for x in ${A[2,-1]}; do REFS+=(--ref $x); done
nice -n 5 python3 -B $R ${A[1]} --ref one14-c1:old $REFS 2>&1 | tail -n 1 | cut -c1-60
sed "s/vers = \[.*\]/vers = ['one11', 'one13', 'one14', 'one15']/" ~/.claude/jobs/e2109d93/tmp/portalcheck.py > ~/.claude/jobs/e2109d93/tmp/portalcheck15.py
python3 ~/.claude/jobs/e2109d93/tmp/portalcheck15.py
