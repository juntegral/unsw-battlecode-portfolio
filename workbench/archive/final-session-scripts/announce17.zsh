#!/bin/zsh
# Post the one16 notice, start the requeue waiter, show the active submission.
T=~/.claude/jobs/e2109d93/tmp
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
wc -c data/guide/px-live-one17.txt
python3 tools/meowbot.py --announce-file data/guide/px-live-one17.txt 2>&1 | tail -n 1 | cut -c1-100
pgrep -f "tmp/requeue17.zsh" > /dev/null || nohup zsh $T/requeue17.zsh > /dev/null 2>&1 &
node tools/submit.js active 2>&1 | tail -1 | cut -c1-60
tail -n 2 data/online/smoke/at-q.log | cut -c1-110
gh pr view 62 --repo forrest-gan2005/battlecode --json state,mergedAt -q '.state + " " + (.mergedAt // "")'
date "+%H:%M:%S"
