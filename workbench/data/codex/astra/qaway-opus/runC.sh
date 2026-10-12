#!/bin/zsh
# qaway-opus: third runner, off and D=7 against mD15.
cd ${0:A:h}
OPP=mD15 ARMS="qa_L qa_7" zsh run_pairs.sh maps/ladder/ladder_around_unsw_1.map:1:1 maps/ladder/ladder_schooltime_2.map:1:0 maps/ladder/ladder_portals_1.map:1:0 maps/ladder/ladder_tower_defense_1.map:1:1 maps/ladder/ladder_australia_1.map:1:0 maps/ladder/ladder_slithery_fight_1.map:1:1 maps/ladder/ladder_trauma_1.map:1:1 maps/ladder/ladder_queen_of_spades_1.map:1:1 > runC.log 2>&1
