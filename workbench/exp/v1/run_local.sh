#!/bin/zsh
# unsw-swarm v1 local check (sanity, not a filter), at most 3 games at a time, nice 10. Opponents proxy4_king, proxy4_swarm, proxy4_elim;
# a layout: maps/online-20260927 seed 1; b layout: maps/server-b seed 2; 60 games per layout and bot.
#   v1   = versions/v1/bot (shipped: BELIEF_FIX_ON, swarm engine)       labels v1-a-px4, v1-b-px4
#   v0t  = exp/v1/bot-fixoff-swf (v0 behaviour + the belief tag)       labels v0t-a-px4, v0t-b-px4
# Slot A: identity part 1 (already running) then v0t-a; slot B: identity part 2 then v0t-b; slot C: v1-a; then v1-b with 2-3 jobs.
cd "$(dirname "$0")/../.."
X=exp/v1
okres() { while true; do m=$(memory_pressure | awk -F': ' '/free percentage/ {gsub("%","",$2); print $2}'); d=$(df -g . | awk 'NR==2 {print $4}'); if [ "${m:-100}" -ge 10 ] && [ "${d:-100}" -ge 20 ]; then return; fi; echo "$(date +%T) pause mem ${m}% disk ${d}G" >> $X/pause.log; sleep 20; done; }
OPPS=proxy4_king,proxy4_swarm,proxy4_elim
(
  while pgrep -f "fingerprint.js --same benchmark exp/v1/bot-fixoff-swf --maps slithery_fight" > /dev/null; do sleep 5; done
  okres; nice -n 10 node tools/eval.js --bot $X/bot-fixoff-swf --label v0t-a-px4 --out $X/v0t-a-px4 --opps $OPPS --seeds 1 --maps maps/online-20260927 --jobs 1 > $X/eval-v0t-a.log 2>&1
  echo done > $X/SLOT-A-DONE
) &
(
  okres; nice -n 10 node tools/fingerprint.js --same benchmark $X/bot-fixoff-swf --maps autarky,portals,prisoners_dilemma,queen_of_spades,trophy --seed 1 > $X/identity/swf-s1-part2.txt 2>&1; echo "exit $?" >> $X/identity/swf-s1-part2.txt
  okres; nice -n 10 node tools/eval.js --bot $X/bot-fixoff-swf --label v0t-b-px4 --out $X/v0t-b-px4 --opps $OPPS --seeds 2 --maps maps/server-b --jobs 1 > $X/eval-v0t-b.log 2>&1
  echo done > $X/SLOT-B-DONE
) &
(
  okres; nice -n 10 node tools/eval.js --bot versions/v1/bot --label v1-a-px4 --out $X/v1-a-px4 --opps $OPPS --seeds 1 --maps maps/online-20260927 --jobs 1 > $X/eval-v1-a.log 2>&1
  echo done > $X/SLOT-C-DONE
  # v1-b: as many jobs as slots are free (A and B may still run)
  J=1; [ -f $X/SLOT-A-DONE ] && J=$((J+1)); [ -f $X/SLOT-B-DONE ] && J=$((J+1))
  okres; nice -n 10 node tools/eval.js --bot versions/v1/bot --label v1-b-px4 --out $X/v1-b-px4 --opps $OPPS --seeds 2 --maps maps/server-b --jobs $J > $X/eval-v1-b.log 2>&1
  echo done > $X/SLOT-C2-DONE
) &
wait
echo done > $X/LOCAL-DONE
