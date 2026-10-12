#!/bin/zsh
# When the running queue runner (live id 21651) has exited, start a new queue for one17 (submission 21693).
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
while pgrep -f "smoke/at-q.sh" > /dev/null; do sleep 20; done
B=data/online/smoke
mv $B/at-q.txt $B/at-q.one16.txt
printf 'one17-c1|-|live one17|952|live\none17-s1|-|live one17|249|live\none17-p1|-|live one17|1101|live\nEND\n' > $B/at-q.txt
LIVE_ID=21693 SMOKE_ALLOW_PENDING=1 nohup $B/at-q.sh > /dev/null 2>&1 &
