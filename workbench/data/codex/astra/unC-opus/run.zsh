#!/bin/zsh
# 3 workers over a prioritised job list; no new game after 14:09 KST
R=$HOME/meow-redteam
maps=(uc_tiny7x7 uc_adj0 uc_tiny9x9_6 uc_tiny7x9 uc_many12 uc_adj1 uc_tiny9x9_2 uc_rich16 uc_thin7x200 uc_thin200x7 uc_sparse3000)
jobs=()
for m in $maps; do jobs+=("mD17 m3base $m uc_mD17 0"); done
for m in $maps; do jobs+=("mD17 mD17 $m uc_mir 0"); done
for m in $maps; do jobs+=("m3base mD17 $m uc_mD17 1"); done
worker() {
  local w=$1 i=0
  for j in $jobs; do
    i=$((i+1))
    (( i % 3 == w )) || continue
    [[ $(date +%H%M) -ge 1409 ]] && break
    local a=(${=j})
    local out=$R/solo/runs/$a[4]/$a[3]-seed1-side$a[5]
    [[ -e $out/result.txt ]] && continue
    mkdir -p $out
    $R/play.sh $R/solo/bots/$a[1] $R/solo/bots/$a[2] $R/maps/un2/$a[3].map 1 $out > $R/solo/runs/$a[4]/$a[3]-side$a[5].stdout 2>&1
  done
}
worker 0 &
worker 1 &
worker 2 &
wait
