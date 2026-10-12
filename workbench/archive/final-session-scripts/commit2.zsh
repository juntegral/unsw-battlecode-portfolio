#!/bin/zsh
# Wrap-up step: bring the write-up, the saved agent reports and the latest session scripts into unsw-swarm and stage them.
S="~/01. Project/개인 프로젝트/unsw-swarm"
T=~/.claude/jobs/e2109d93/tmp
rsync -a --exclude 'remote-heads.txt' --exclude 'rel/' --exclude 'rel.log' --exclude 'idx-*' --exclude 'zt.txt' $T/ "$S/archive/final-session-scripts/"
wc -l "$S"/docs/retro/*.md | cut -c1-120
git -C "$S" add -A
find "$S/data/retro-work" -type f -size -1000k \( -name '*.py' -o -name '*.md' -o -name '*.txt' -o -name '*.tsv' -o -name '*.json' -o -name '*.csv' \) -print0 | (cd "$S" && xargs -0 git add -f) 2>&1 | tail -n 2
python3 -B $T/scan.py "$S" --staged | tail -n 5
git -C "$S" diff --cached --stat | tail -n 1
