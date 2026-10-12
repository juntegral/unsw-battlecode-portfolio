#!/bin/zsh
# other-map check for tr_skt, side 0 against m3base, 2 games at a time; off arms for ladder maps exist in tr_mD17_v3
G="~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/trauma-opus/g.zsh"
M=~/meow-redteam/maps
R=~/meow-redteam/solo/runs
until [[ -f $R/tr_skt_v3/ladder_traumafast_1-seed1-side1/result.txt && -f $R/tr_skt_v3/ladder_trauma_1-seed1-side1/result.txt ]]; do sleep 2; done
zsh $G skt_v3 tr_skt m3base $M/ladder/ladder_default_1.map 0 &
zsh $G skt_v3 tr_skt m3base $M/ladder/ladder_australia_1.map 0 &
wait
zsh $G skt_v3 tr_skt m3base $M/ladder/ladder_queen_of_spades_1.map 0 &
zsh $G skt_v3 tr_skt m3base $M/ladder/ladder_stripes_1.map 0 &
wait
zsh $G skt_v3 tr_skt m3base $M/ladder/ladder_portals_1.map 0 &
zsh $G skt_v3 tr_skt m3base $R/tr_maps/ladder_traumafast_1.map 0 &
wait
zsh $G mD17_v3 mD17 m3base $M/gx/gx_islands_24x12_911201.map 0 &
zsh $G skt_v3 tr_skt m3base $M/gx/gx_islands_24x12_911201.map 0 &
wait
zsh $G mD17_v3 mD17 m3base $M/gx/gx_open_24x12_910901.map 0 &
zsh $G skt_v3 tr_skt m3base $M/gx/gx_open_24x12_910901.map 0 &
wait
echo batch2-done
