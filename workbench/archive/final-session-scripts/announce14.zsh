#!/bin/zsh
# Post the one14 notice to #meow through meowbot.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
wc -c data/guide/px-live-one14.txt
python3 tools/meowbot.py --announce-file data/guide/px-live-one14.txt 2>&1 | tail -n 1 | cut -c1-100
