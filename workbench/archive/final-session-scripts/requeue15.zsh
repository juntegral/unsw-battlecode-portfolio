#!/bin/zsh
# When the running queue runner (live id 21497) has exited, start a new queue for one15 (submission 21583).
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
while pgrep -f "smoke/at-q.sh" > /dev/null; do sleep 20; done
B=data/online/smoke
mv $B/at-q.txt $B/at-q.one14.txt
printf 'one15-c1|-|live one15|952|live\none15-p1|-|live one15|1101|live\none15-s1|-|live one15 against a peer that beat one14 4-1|249|live\none15-q1|-|live one15 against a lower team that beat one13 4-1|501|live\nEND\n' > $B/at-q.txt
LIVE_ID=21583 SMOKE_ALLOW_PENDING=1 nohup $B/at-q.sh > /dev/null 2>&1 &
