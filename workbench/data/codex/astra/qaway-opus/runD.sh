#!/bin/zsh
# qaway-opus: drain runner C (empty out dirs = skipped), wait for it, play one instrumented game, then C's remaining specs.
cd ${0:A:h}
R=$HOME/meow-redteam
S=$R/solo
REST=(ladder_portals_1:1:0 ladder_tower_defense_1:1:1 ladder_australia_1:1:0 ladder_slithery_fight_1:1:1 ladder_trauma_1:1:1 ladder_queen_of_spades_1:1:1)
for spec in $REST; do
  n=${spec%%:*}; rest=${spec#*:}; seed=${rest%%:*}; side=${rest#*:}
  for arm in qa_L qa_7; do
    [ -e $S/runs/${arm}_mD15/$n-seed$seed-side$side ] || mkdir -p $S/runs/${arm}_mD15/$n-seed$seed-side$side
  done
done
until grep -q queen_of_spades runC.log; do sleep 3; done
mkdir -p $S/runs/qa_dbg_mD15
$R/play.sh $S/bots/mD15 $S/bots/qa_dbg $R/maps/ladder/ladder_around_unsw_1.map 1 $S/runs/qa_dbg_mD15/ladder_around_unsw_1-seed1-side1 > $S/runs/qa_dbg_mD15/around.log 2>&1
echo "$(date +%H:%M:%S) debug game done" >> runD.log
for spec in $REST; do
  n=${spec%%:*}; rest=${spec#*:}; seed=${rest%%:*}; side=${rest#*:}
  for arm in qa_L qa_7; do
    rmdir $S/runs/${arm}_mD15/$n-seed$seed-side$side 2>/dev/null
  done
  OPP=mD15 ARMS="qa_L qa_7" zsh run_pairs.sh maps/ladder/$n.map:$seed:$side >> runD.log 2>&1
done
