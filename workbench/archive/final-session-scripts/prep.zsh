#!/bin/zsh
# Wrap-up step A: copy session-only material to a durable folder inside unsw-swarm (archive/), look at the loop runner,
# and measure replay compression. Nothing is deleted.
S="~/01. Project/개인 프로젝트/unsw-swarm"
B="~/01. Project/개인 프로젝트/battlecode"
T=~/.claude/jobs/e2109d93/tmp
mkdir -p "$S/archive/final-session-scripts" "$S/archive/claude-memory" "$S/archive/claude-rules"
rsync -a --exclude 'remote-heads.txt' --exclude '*.tar*' --exclude 'rel/' $T/ "$S/archive/final-session-scripts/"
rsync -a ~/.claude/projects/-Users-jun-01--Project---------battlecode/memory/ "$S/archive/claude-memory/"
cp "$B/CLAUDE.local.md" "$S/archive/claude-rules/CLAUDE.local.md"
echo "archive: $(find "$S/archive" -type f | wc -l | tr -d ' ') files, $(du -sh "$S/archive" | cut -f1)"
echo "=== loop runner"
ps -o pid,ppid,etime,command -p 75232,75233,79153,79160 | cut -c1-150
echo "children of runner: $(pgrep -P 75232 | tr '\n' ' ')"
ls -la "$B/nohup.out" | cut -c1-90; tail -n 3 "$B/nohup.out" | cut -c1-160
echo "=== compression test"
F="$S/data/online/live-one1/b1532570/M1532570.replay"
ls -l "$F" | awk '{print "raw", $5}'
/usr/bin/time -p zstd -T0 -19 --long=27 -c "$F" 2> $T/zt.txt | wc -c | awk '{print "zstd19", $1}'; grep real $T/zt.txt
/usr/bin/time -p zstd -T0 -10 --long=27 -c "$F" 2> $T/zt.txt | wc -c | awk '{print "zstd10", $1}'; grep real $T/zt.txt
/usr/bin/time -p xz -T0 -6 -c "$F" 2> $T/zt.txt | wc -c | awk '{print "xz6", $1}'; grep real $T/zt.txt
