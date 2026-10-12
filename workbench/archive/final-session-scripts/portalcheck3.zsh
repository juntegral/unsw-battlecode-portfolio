#!/bin/zsh
# Build the label reports of the one14 sets that exist so their rows are in the cache, then print pearls by r100 per map.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
R=data/analysis/ladder/dossier/online/label_report.py
A=()
for l in c1 p1 k1; do [ -f data/online/smoke/one14-$l-result.txt ] && A+=(one14-$l:old); done
[ ${#A} -eq 0 ] && exit 0
REFS=()
for x in ${A[2,-1]}; do REFS+=(--ref $x); done
nice -n 5 python3 -B $R ${A[1]} --ref one11-c1:old $REFS 2>&1 | tail -n 1 | cut -c1-60
python3 ~/.claude/jobs/e2109d93/tmp/portalcheck.py
