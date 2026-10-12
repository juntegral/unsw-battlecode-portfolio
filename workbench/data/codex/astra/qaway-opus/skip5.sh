#!/bin/zsh
# qaway-opus: D=5 replays were identical to off in the first two specs; skip that arm for the rest (empty out dir = skipped).
cd $HOME/meow-redteam/solo/runs
for n in ladder_maze_1-seed1-side0 ladder_trophy_1-seed1-side1 ladder_stripes_1-seed1-side0 ladder_weakhold_1-seed1-side1 ladder_devil_1-seed1-side0 ladder_schooltime_1-seed1-side1 gx_rooms_24x64_911003-seed1-side0 gx_islands_64x16_911202-seed1-side1; do
  [ -e qa_5_mD15/$n ] || mkdir -p qa_5_mD15/$n
done
for n in gx_open_24x12_910901-seed1-side1 gx_corridors_64x16_911102-seed1-side0 ladder_australia_1-seed1-side1 ladder_slithery_fight_1-seed1-side0 gx_ring_24x64_911303-seed1-side1 ladder_trauma_1-seed1-side0 gx_rotation_64x16_911402-seed1-side1 ladder_queen_of_spades_1-seed1-side0; do
  [ -e qa_5_m3base/$n ] || mkdir -p qa_5_m3base/$n
done
