#!/bin/zsh
# Post the one15 notice to #meow through meowbot and show the active submission.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
wc -c data/guide/px-live-one15.txt
python3 tools/meowbot.py --announce-file data/guide/px-live-one15.txt 2>&1 | tail -n 1 | cut -c1-100
node tools/submit.js active 2>&1 | tail -1 | cut -c1-60
date "+%H:%M:%S"
