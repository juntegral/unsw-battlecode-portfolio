#!/bin/zsh
# other-map check, side 0 against m3base, off (mD17) and on (tr_pfd13), 4 games at a time
G="~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/trauma-opus/g.zsh"
M=~/meow-redteam/maps
maps=($M/ladder/ladder_portals_1.map $M/ladder/ladder_queen_of_spades_1.map $M/ladder/ladder_australia_1.map $M/ladder/ladder_default_1.map $M/ladder/ladder_stripes_1.map $M/gx/gx_islands_64x16_911202.map $M/gx/gx_islands_24x12_911201.map)
n=0
for m in $maps; do
  zsh $G mD17_v3 mD17 m3base $m 0 &
  zsh $G pfd13_v3 tr_pfd13 m3base $m 0 &
  n=$((n+2))
  if (( n % 4 == 0 )); then wait; fi
done
wait
echo batch-done
