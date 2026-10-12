#!/bin/zsh
# second queue, 2 workers; "botA botB map mapdir arm side"; no new game after 14:09 KST
R=$HOME/meow-redteam
jobs=(
"uc_nfc m3base uc_sparse3000 un2 uc_nfc 0"
"uc_nlf m3base uc_sparse3000 un2 uc_nlf 0"
"m3base mD17 uc_tiny7x7 un2 uc_mD17 1"
"uc_nqh m3base uc_sparse3000 un2 uc_nqh 0"
"m3base mD17 uc_tiny7x9 un2 uc_mD17 1"
"uc_nqb m3base uc_sparse3000 un2 uc_nqb 0"
"m3base mD17 uc_sparse3000 un2 uc_mD17 1"
"mD17 mD17 uc_tiny7x9 un2 uc_mir 0"
"uc_nfe m3base uc_sparse3000 un2 uc_nfe 0"
"uc_nam m3base uc_sparse3000 un2 uc_nam 0"
"uc_ns0 m3base gx_corridors_7x7_911100 gx uc_ns0 0"
"mD16 m3base uc_rich16 un2 uc_mD16 0"
"mD17 mD17 uc_sparse3000 un2 uc_mir 0"
)
worker() {
  local w=$1 i=0
  for j in $jobs; do
    i=$((i+1))
    (( i % 2 == w )) || continue
    [[ $(date +%H%M) -ge 1409 ]] && break
    local a=(${=j})
    local out=$R/solo/runs/$a[5]/$a[3]-seed1-side$a[6]
    [[ -e $out/result.txt ]] && continue
    mkdir -p $out
    $R/play.sh $R/solo/bots/$a[1] $R/solo/bots/$a[2] $R/maps/$a[4]/$a[3].map 1 $out > $R/solo/runs/$a[5]/$a[3]-side$a[6].stdout 2>&1
  done
}
worker 0 &
worker 1 &
wait
