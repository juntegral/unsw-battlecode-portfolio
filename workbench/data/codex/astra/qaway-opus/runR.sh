#!/bin/zsh
# qaway-opus: QUEEN_OUT_OF_REACH arms; $1 = runner number. Off games (qa_L) from the first round are reused where they exist.
cd ${0:A:h}
L=maps/ladder/ladder_
case $1 in
1) OPP=mD15 ARMS="qa_r1 qa_r3" zsh run_pairs.sh ${L}slithery_fight_1.map:1:1 ${L}islands_1.map:1:1 ${L}stripes_1.map:1:0 ${L}weakhold_1.map:1:1 ${L}australia_1.map:1:0 ${L}queen_of_spades_1.map:1:1 ${L}devil_1.map:1:0 ${L}schooltime_2.map:1:0 > runR1.log 2>&1 ;;
2) OPP=mD15 ARMS="qa_r1 qa_r3" zsh run_pairs.sh ${L}default_1.map:1:0 ${L}tower_defense_1.map:1:1 ${L}trophy_1.map:1:1 ${L}around_unsw_1.map:1:1 ${L}maze_1.map:1:0 maps/gx/gx_islands_64x16_911202.map:1:1 maps/gx/gx_rooms_24x64_911003.map:1:0 ${L}trauma_1.map:1:1 > runR2.log 2>&1 ;;
3) OPP=mD15 ARMS="qa_L qa_r3" zsh run_pairs.sh ${L}slithery_fight_1.map:2:1 ${L}slithery_fight_1.map:1:0 ${L}slithery_fight_1.map:2:0 ${L}slithery_fight_1.map:3:1 > runR3.log 2>&1
   OPP=m3base ARMS="qa_r1 qa_r3" zsh run_pairs.sh ${L}slithery_fight_1.map:1:0 ${L}tower_defense_1.map:1:0 maps/gx/gx_open_24x12_910901.map:1:1 maps/gx/gx_corridors_64x16_911102.map:1:0 >> runR3.log 2>&1 ;;
esac
