#!/bin/zsh
# Which ranked requests are allowed now, and how many tickets are left (no request is sent).
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
node tools/online.js request 249,62,1149,1059,1148,899,19 --ranked --purpose "check" 2>&1 | grep "가능\|불가\|남음\|우리:" | cut -c1-170
date "+%H:%M:%S"
