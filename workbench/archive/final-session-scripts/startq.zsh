#!/bin/zsh
# Start the online queue runner for the live bot one14 (submission 21497), detached.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
LIVE_ID=21497 SMOKE_ALLOW_PENDING=1 nohup data/online/smoke/at-q.sh > /dev/null 2>&1 &
sleep 4
tail -n 2 data/online/smoke/at-q.log | cut -c1-100
head -n 2 data/online/smoke/one13-q1-result.txt | cut -c1-100
