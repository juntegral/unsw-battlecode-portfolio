#!/bin/zsh
# More ranked requests with the live bot against the three teams we have just beaten again (as many as tickets allow).
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
ID=$(node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}')
echo "active $ID"
node tools/online.js request 249,19,1148 --ranked --purpose "check" 2>&1 | grep "가능\|불가\|남음" | cut -c1-170
N=$(node tools/online.js tickets --json 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin)['normal'];print(60-max(d['fromServer'],d['fromLedger']))")
echo "tickets by the stricter count: $N"
L=""
[ "$N" -ge 5 ] && L="249"
[ "$N" -ge 10 ] && L="249,19"
[ "$N" -ge 15 ] && L="249,19,1148"
[ -n "$L" ] && node tools/online.js request $L --ranked --purpose "ranked scrim with the live bot against teams it has just beaten again (jun's call)" --expect-active $ID --confirm 2>&1 | grep "신청됨\|불가\|사용한\|실패" | cut -c1-170
date "+%H:%M:%S"
