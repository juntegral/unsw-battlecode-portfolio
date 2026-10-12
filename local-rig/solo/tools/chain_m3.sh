#!/bin/zsh
# Night chain on the newest main (main3): identity, spawn clear, bundles. Waits for any running batch first.
cd ~/meow-redteam || exit 1
while pgrep -f "solo/tools/run_arms.sh" >/dev/null; do sleep 20; done
ALL="$(ls maps/dev/*.map maps/eval/*.map maps/ladder/ladder_islands_1.map maps/ladder/ladder_australia_1.map maps/ladder/ladder_schooltime_1.map maps/ladder/ladder_schooltime_2.map maps/ladder/ladder_around_unsw_1.map maps/ladder/ladder_portals_1.map maps/ladder/ladder_tower_defense_1.map maps/ladder/ladder_stripes_1.map | tr '\n' ' ')"
LAD="maps/ladder/ladder_islands_1.map maps/ladder/ladder_australia_1.map maps/ladder/ladder_schooltime_1.map maps/ladder/ladder_schooltime_2.map maps/ladder/ladder_around_unsw_1.map maps/ladder/ladder_portals_1.map maps/ladder/ladder_tower_defense_1.map maps/ladder/ladder_stripes_1.map"
rm -rf solo/runs/ident3
for m in eval/sqheld_islands_medium_90038 dev/sqheld_portals_medium_90007 eval/sqheld_portalrooms_small_90021; do n=${m#*/}
  ./play.sh solo/bots/m3base bot maps/$m.map 7 solo/runs/ident3/m3base-$n-0 >/dev/null 2>&1 &
  ./play.sh solo/bots/m3zero bot maps/$m.map 7 solo/runs/ident3/m3zero-$n-0 >/dev/null 2>&1 &
  wait
done
SOLO_MAPS="$ALL" ./solo/tools/run_arms.sh 1 m3base m3sc
SOLO_MAPS="$ALL" ./solo/tools/run_arms.sh 1 m3b6
SOLO_MAPS="$LAD" ./solo/tools/run_arms.sh 2 m3base m3sc m3b6
SOLO_MAPS="$ALL" ./solo/tools/run_arms.sh 1 m3b5
echo "chain_m3 done $(date '+%F %T')" >> solo/runs/run.log
