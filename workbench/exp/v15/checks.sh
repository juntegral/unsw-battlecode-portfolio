#!/bin/zsh
# v1.5 checks (versions/v1.5/VERSION.md §3 a-c, e, f), one game at a time, after the v1.4 hold identity (exp/v14/IDENTITY-HOLD-DONE).
# Each step writes its own file; a step whose DONE marker exists is skipped (resumable after a sleep or a kill).
cd "$(dirname "$0")/../.."
X=exp/v15
until [ -f exp/v14/IDENTITY-HOLD-DONE ]; do sleep 20; done
diskok() { [ "$(df -g / | awk 'NR==2 {print $4}')" -ge 21 ]; }
step() { [ -f $X/$1.DONE ] && return 0; diskok || { echo "disk < 21 GB: stop"; exit 1; }; shift_name=$1; shift; "$@" > $X/$shift_name.txt 2>&1; echo "exit $?" >> $X/$shift_name.txt; echo done > $X/$shift_name.DONE; }
# (a) OPENING_ON off = v1.3
step id-a-s1 nice -n 10 node tools/fingerprint.js --same versions/v1.3/bot exp/v15/bot-opoff --maps autarky,prisoners_dilemma,portals,devil,schooltime,slithery_fight,trauma --seed 1
step id-a-s2 nice -n 10 node tools/fingerprint.js --same versions/v1.3/bot exp/v15/bot-opoff --maps autarky,prisoners_dilemma,portals,devil,schooltime,slithery_fight,trauma --seed 2
# (b) OPENING_ON on = v1.3 on maps without a script
step id-b-s1 nice -n 10 node tools/fingerprint.js --same versions/v1.3/bot versions/v1.5/bot --maps autarky,prisoners_dilemma,portals,trauma,queen_of_spades --seed 1
step id-b-s2 nice -n 10 node tools/fingerprint.js --same versions/v1.3/bot versions/v1.5/bot --maps autarky,prisoners_dilemma,portals,trauma,queen_of_spades --seed 2
step id-b-b node exp/v15/fp.js versions/v1.3/bot versions/v1.5/bot --maps maps/server-b/queen_of_spades_b.map,maps/server-b/prisoners_dilemma_10.map --sides A,B --seeds 1,2
# (c) maps with only the opening: v1.5 = v1.4 (the v1.4 local results carry over)
step id-c-s1 nice -n 10 node tools/fingerprint.js --same versions/v1.4/bot versions/v1.5/bot --maps devil,trophy,schooltime,default --seed 1
step id-c-s2 nice -n 10 node tools/fingerprint.js --same versions/v1.4/bot versions/v1.5/bot --maps devil,trophy,schooltime,default --seed 2
step id-c-b node exp/v15/fp.js versions/v1.4/bot versions/v1.5/bot --maps maps/server-b/devil_b.map,maps/server-b/schooltime_b.map --sides A,B --seeds 1,2
# (e) CPU: our points per turn, side A against proxy4_swarm, seed 1
mkdir -p $X/cpu
for m in online-20260927/default online-20260927/schooltime online-20260927/slithery_fight server-b/slithery_fight_b online-20260927/trauma online-20260927/devil; do
  n=$(basename $m); [ -f $X/cpu/$n.txt ] && continue; diskok || exit 1
  (cd $X/cpu && nice -n 10 ../../../tools/unswbc run ../../../maps/$m.map ../../../versions/v1.5/bot ../../../bots/proxy4_swarm --sandbox --seed 1 --no-logs --no-draw -o $n.replay > $n.log 2>&1;
   grep -i "points per turn\|error\|timed out\|no reply\|exceeded\|wins" $n.log > $n.txt; rm -f $n.replay)
done
# (f) the upload smoke replica
step smoke-upload-v15 nice -n 10 node exp/v1/smoke_upload.js versions/v1.5/bot
echo done > $X/CHECKS-DONE
