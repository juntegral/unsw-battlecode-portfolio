#!/bin/zsh
cd ~/meow-redteam || exit 1
while pgrep -f "solo/tools/run_arms.sh" >/dev/null; do sleep 20; done
ALL="$(ls maps/dev/*.map maps/eval/*.map maps/ladder/ladder_islands_1.map maps/ladder/ladder_australia_1.map maps/ladder/ladder_schooltime_1.map maps/ladder/ladder_schooltime_2.map maps/ladder/ladder_around_unsw_1.map maps/ladder/ladder_portals_1.map maps/ladder/ladder_tower_defense_1.map maps/ladder/ladder_stripes_1.map | tr '\n' ' ')"
SOLO_MAPS="$ALL" SOLO_OPP=solo/bots/m3base ./solo/tools/run_arms.sh 1 m3b7_vb
echo "mirror b7 done $(date '+%F %T')" >> solo/runs/run.log
SOLO_MAPS="$ALL" ./solo/tools/run_arms.sh 2 m3ce m3b8
echo "chain_m3c done $(date '+%F %T')" >> solo/runs/run.log
