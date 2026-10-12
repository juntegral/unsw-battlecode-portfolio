#!/bin/zsh
# stack11 local check, at most 3 games at a time. Opponents proxy4_king, proxy4_swarm, proxy4_elim; a layout seed 1, b layout seed 2.
#   slot 1 (one game at a time): the all-off fingerprint against stack10 (portals, slithery_fight), the PROFILE build against proxy4_swarm on
#     Slithery Fight and Schooltime b (max decide() points per turn), then the b-layout eval against proxy4_elim (label stack11-b-px4-elim).
#   slots 2-3 (two at a time): the a-layout eval (stack11-a-px4), then the b-layout eval against proxy4_king and proxy4_swarm (stack11-b-px4-ks).
# eval.js stops starting games below 20 GiB of free disk. Firing and safety only (not G).
cd "~/01. Project/개인 프로젝트/unsw-heuristic"
X=exp/cand-stack11
one() { local m=$1; local n=$(basename $m .map); mkdir -p $X/prof/$n && (cd $X/prof/$n && nice -n 5 "../../../../tools/unswbc" run "../../../../$m" "../../bot-prof" "../../../../bots/proxy4_swarm" --sandbox --seed 1 --no-logs --no-draw -o game.replay > run.log 2>&1); }
(
  node tools/fingerprint.js --same exp/cand-stack10/bot $X/bot-off --maps portals,slithery_fight > $X/fingerprint-off.log 2>&1
  echo done > $X/FP-DONE
  for m in maps/online-20260927/slithery_fight.map maps/server-b/schooltime_b.map; do one $m; done
  echo done > $X/prof/DONE
  node tools/eval.js --bot $X/bot --label stack11-b-px4-elim --opps proxy4_elim --seeds 2 --maps maps/server-b --jobs 1 > $X/eval-b-elim.log 2>&1
  echo done > $X/SLOT1-DONE
) &
S1=$!
node tools/eval.js --bot $X/bot --label stack11-a-px4 --opps proxy4_king,proxy4_swarm,proxy4_elim --seeds 1 --maps maps/online-20260927 --jobs 2 > $X/eval-a.log 2>&1
echo done > $X/LOCAL-A-DONE
node tools/eval.js --bot $X/bot --label stack11-b-px4-ks --opps proxy4_king,proxy4_swarm --seeds 2 --maps maps/server-b --jobs 2 > $X/eval-b-ks.log 2>&1
wait $S1
echo done > $X/LOCAL-DONE
