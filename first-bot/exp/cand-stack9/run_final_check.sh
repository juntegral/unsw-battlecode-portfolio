#!/bin/zsh
# final W10 build (l340; F2p and ce off after the W9 verdict): quick games vs proxy4_king to confirm it builds, fires cl / lsplit / fc / cov
# and shows no ce / Fp tags. Two at a time (the all-off fingerprint may still run one game), then the third.
cd "~/01. Project/개인 프로젝트/unsw-heuristic"
one() { local m=$1 s=$2; local n=$(basename $m .map)_$s; mkdir -p exp/cand-stack9/final-check/$n && (cd exp/cand-stack9/final-check/$n && "../../../../tools/unswbc" run "../../../../$m" "../../bot" "../../../../bots/proxy4_king" --sandbox --seed $s --no-logs --no-draw -o game.replay > run.log 2>&1; echo "exit $?" >> run.log); }
one maps/online-20260927/portals.map 1 &
one maps/online-20260927/slithery_fight.map 1 &
wait
one maps/online-20260927/trauma.map 1
echo done > exp/cand-stack9/final-check/DONE
