#!/bin/zsh
# third worker: the two tail jobs of run2
R=$HOME/meow-redteam
o=$R/solo/runs/uc_ns0/gx_corridors_7x7_911100-seed1-side0
if [[ ! -e $o ]]; then mkdir -p $o; $R/play.sh $R/solo/bots/uc_ns0 $R/solo/bots/m3base $R/maps/gx/gx_corridors_7x7_911100.map 1 $o > $R/solo/runs/uc_ns0/c7.stdout 2>&1; fi
o=$R/solo/runs/uc_nqb/uc_sparse3000-seed1-side0
if [[ ! -e $o ]]; then mkdir -p $o; $R/play.sh $R/solo/bots/uc_nqb $R/solo/bots/m3base $R/maps/un2/uc_sparse3000.map 1 $o > $R/solo/runs/uc_nqb/uc_sparse3000-side0.stdout 2>&1; fi
