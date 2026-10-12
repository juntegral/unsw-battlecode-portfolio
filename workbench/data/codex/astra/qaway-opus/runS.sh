#!/bin/zsh
# qaway-opus: QUEEN_OUT_OF_REACH second form (farthest-out cell, queens with 2+ free steps); $1 = runner number. Off = qa_L.
cd ${0:A:h}
L=maps/ladder/ladder_
case $1 in
1) OPP=mD15 ARMS="qa_s1 qa_s3" zsh run_pairs.sh ${L}slithery_fight_1.map:1:1 ${L}slithery_fight_1.map:2:1 ${L}slithery_fight_1.map:1:0 ${L}slithery_fight_1.map:2:0 ${L}slithery_fight_1.map:3:1 ${L}islands_1.map:1:1 ${L}queen_of_spades_1.map:1:1 ${L}australia_1.map:1:0 ${L}schooltime_2.map:1:0 > runS1.log 2>&1 ;;
2) OPP=mD15 ARMS="qa_s1 qa_s3" zsh run_pairs.sh ${L}default_1.map:1:0 ${L}tower_defense_1.map:1:1 ${L}trophy_1.map:1:1 ${L}stripes_1.map:1:0 ${L}weakhold_1.map:1:1 ${L}devil_1.map:1:0 ${L}around_unsw_1.map:1:1 ${L}maze_1.map:1:0 maps/gx/gx_islands_64x16_911202.map:1:1 maps/gx/gx_rooms_24x64_911003.map:1:0 ${L}trauma_1.map:1:1 > runS2.log 2>&1 ;;
3) OPP=m3base ARMS="qa_s1 qa_s3" zsh run_pairs.sh ${L}slithery_fight_1.map:1:0 ${L}tower_defense_1.map:1:0 maps/gx/gx_open_24x12_910901.map:1:1 maps/gx/gx_corridors_64x16_911102.map:1:0 ${L}australia_1.map:1:1 ${L}trauma_1.map:1:0 maps/gx/gx_rotation_64x16_911402.map:1:1 ${L}queen_of_spades_1.map:1:0 maps/gx/gx_ring_24x64_911303.map:1:1 ${L}portals_1.map:1:1 > runS3.log 2>&1 ;;
4) OPP=mD15 ARMS="qa_L qa_s1 qa_s3" zsh run_pairs.sh ${L}slithery_fight_1.map:3:0 ${L}slithery_fight_1.map:4:1 ${L}slithery_fight_1.map:4:0 ${L}slithery_fight_1.map:5:1 ${L}slithery_fight_1.map:5:0 ${L}slithery_fight_1.map:6:1 > runS4.log 2>&1 ;;
esac
