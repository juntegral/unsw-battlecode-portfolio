#!/bin/zsh
# head to head tr_skt against mD17, both seats, 2 games at a time
G="~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/trauma-opus/g.zsh"
M=~/meow-redteam/maps
for m in $M/ladder/ladder_portals_1.map $M/ladder/ladder_trauma_1.map $M/ladder/ladder_australia_1.map $M/ladder/ladder_default_1.map; do
  zsh $G skt_vD tr_skt mD17 $m 0 &
  zsh $G skt_vD tr_skt mD17 $m 1 &
  wait
done
echo batch3-done
