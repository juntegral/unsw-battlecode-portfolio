#!/bin/zsh
cd "~/01. Project/개인 프로젝트/unsw-swarm"
until [ "$(date +%Y%m%d%H%M)" -ge 202610050037 ]; do sleep 30; done
exec data/online/smoke/run-pair.sh passage2-test "~/01. Project/개인 프로젝트/battlecode/tune_runs/ab2/PASSAGE27B" "#27 passage (queen excluded)"
