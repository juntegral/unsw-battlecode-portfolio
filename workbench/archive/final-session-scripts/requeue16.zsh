#!/bin/zsh
# When the running queue runner (live id 21583) has exited, start a new queue for one16 (submission 21651).
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
while pgrep -f "smoke/at-q.sh" > /dev/null; do sleep 20; done
B=data/online/smoke
mv $B/at-q.txt $B/at-q.one15.txt
printf 'one16-c1|-|live one16|952|live\none16-p1|-|live one16|1101|live\none16-s1|-|live one16|249|live\none16-q1|-|live one16|501|live\nEND\n' > $B/at-q.txt
LIVE_ID=21651 SMOKE_ALLOW_PENDING=1 nohup $B/at-q.sh > /dev/null 2>&1 &
