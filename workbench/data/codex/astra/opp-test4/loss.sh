#!/bin/zsh
cd "~/01. Project/개인 프로젝트/unsw-swarm"
O=data/codex/astra/opp-test4
python3 -B data/codex/astra/loss15-sonnet/l15.py 1501265 1501267 1535543 1535547 > $O/l15-loss.txt 2>&1
python3 -B data/codex/astra/loss15-sonnet/qtrace.py 1501265 109 117 > $O/qt-1501265.txt 2>&1
python3 -B data/codex/astra/loss15-sonnet/qtrace.py 1501267 337 345 > $O/qt-1501267.txt 2>&1
python3 -B data/codex/astra/loss15-sonnet/qtrace.py 1535543 85 97 > $O/qt-1535543.txt 2>&1
python3 -B data/codex/astra/loss15-sonnet/qtrace.py 1535547 147 155 > $O/qt-1535547.txt 2>&1
date
