#!/bin/zsh
# Ranked requests with the live bot one18 (21761) against five teams we have beaten more often than their rating predicts.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
node tools/online.js request 249,19,1149,1148,899 --ranked --purpose "ranked scrim with the live bot one18 against teams we have beaten more often than the rating expects (jun's call, target seed mid 2200s)" --expect-active 21761 --confirm 2>&1 | grep "신청됨\|불가\|사용한\|실패\|오류" | cut -c1-170
date "+%H:%M:%S"
