#!/bin/zsh
cd "~/01. Project/개인 프로젝트/unsw-heuristic"
D=exp/cand-stack12/mccheck
( time nice -n 10 node tools/mech_check.dev12.js cand-stack1-online --jobs 1 --cases 1 --out $D/s1-dev.md ) > $D/s1-dev.log 2>&1
( time nice -n 10 node tools/mech_check.js cand-merge2-online-r3 --jobs 2 --out $D/r3-base.md ) > $D/r3-base.log 2>&1 &
( time nice -n 10 node tools/mech_check.dev12.js cand-merge2-online-r3 --jobs 2 --out $D/r3-dev.md ) > $D/r3-dev.log 2>&1
wait
echo done > $D/DONE
