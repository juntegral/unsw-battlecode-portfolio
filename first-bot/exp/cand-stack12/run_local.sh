#!/bin/zsh
# stack12 local check (firing and safety only, not G), at most 3 games at a time. Opponents proxy4_king, proxy4_swarm, proxy4_elim; a layout seed 1
# (maps/online-20260927), b layout seed 2 (maps/server-b).
#   slot 1 (one game at a time): the all-off fingerprint against stack11 (portals, slithery_fight), the pf-on fingerprint against stack11 on the pf-off
#     maps (autarky, portals, prisoners_dilemma), the PROFILE build against proxy4_swarm on Slithery Fight a and Schooltime b, the b-layout pf-on eval
#     against proxy4_elim (stack12-b-px4-elim), then the all-off baseline on the seven pf maps, b layout (stack12off-b-pf).
#   slots 2-3 (two at a time): the a-layout pf-on eval (stack12-a-px4), the b-layout pf-on eval against proxy4_king and proxy4_swarm (stack12-b-px4-ks),
#     then the all-off baseline on the seven pf maps, a layout (stack12off-a-pf). The pf-off maps need no baseline run: pf-on is identical there.
# Before each step: wait while free memory < 10% or free disk < 20 GiB (eval.js also stops starting games below 20 GiB).
cd "~/01. Project/개인 프로젝트/unsw-heuristic"
X=exp/cand-stack12
okres() { while true; do m=$(memory_pressure | awk -F': ' '/free percentage/ {gsub("%","",$2); print $2}'); d=$(df -g . | awk 'NR==2 {print $4}'); if [ "${m:-100}" -ge 10 ] && [ "${d:-100}" -ge 20 ]; then return; fi; echo "$(date +%T) pause mem ${m}% disk ${d}G" >> $X/pause.log; sleep 20; done; }
one() { local m=$1; local n=$(basename $m .map); mkdir -p $X/prof/$n && (cd $X/prof/$n && nice -n 5 "../../../../tools/unswbc" run "../../../../$m" "../../bot-prof" "../../../../bots/proxy4_swarm" --sandbox --seed 1 --no-logs --no-draw -o game.replay > run.log 2>&1); }
(
  okres; node tools/fingerprint.js --same exp/cand-stack11/bot $X/bot-off --maps portals,slithery_fight > $X/fingerprint-off.log 2>&1
  echo done > $X/FP-OFF-DONE
  okres; node tools/fingerprint.js --same exp/cand-stack11/bot $X/bot --maps autarky,portals,prisoners_dilemma > $X/fingerprint-offmaps.log 2>&1
  echo done > $X/FP-ON-DONE
  okres; for m in maps/online-20260927/slithery_fight.map maps/server-b/schooltime_b.map; do one $m; done
  echo done > $X/prof/DONE
  okres; node tools/eval.js --bot $X/bot --label stack12-b-px4-elim --opps proxy4_elim --seeds 2 --maps maps/server-b --jobs 1 > $X/eval-b-elim.log 2>&1
  echo done > $X/B-ELIM-DONE
  okres; node tools/eval.js --bot $X/bot-off --label stack12off-b-pf --opps proxy4_king,proxy4_swarm,proxy4_elim --seeds 2 --maps $X/maps-pf-b --jobs 1 > $X/eval-off-b.log 2>&1
  echo done > $X/SLOT1-DONE
) &
S1=$!
okres; node tools/eval.js --bot $X/bot --label stack12-a-px4 --opps proxy4_king,proxy4_swarm,proxy4_elim --seeds 1 --maps maps/online-20260927 --jobs 2 > $X/eval-a.log 2>&1
echo done > $X/A-DONE
okres; node tools/eval.js --bot $X/bot --label stack12-b-px4-ks --opps proxy4_king,proxy4_swarm --seeds 2 --maps maps/server-b --jobs 2 > $X/eval-b-ks.log 2>&1
echo done > $X/B-KS-DONE
okres; node tools/eval.js --bot $X/bot-off --label stack12off-a-pf --opps proxy4_king,proxy4_swarm,proxy4_elim --seeds 1 --maps $X/maps-pf-a --jobs 2 > $X/eval-off-a.log 2>&1
echo done > $X/OFF-A-DONE
wait $S1
echo done > $X/LOCAL-DONE
