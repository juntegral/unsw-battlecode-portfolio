#!/bin/zsh
cd "~/01. Project/개인 프로젝트/unsw-swarm"
until [ -f data/online/smoke/passage2-test-finished ]; do sleep 30; done
[ "$(python3 -c "import json;print(json.load(open('data/online/smoke/passage2-test.json')).get('phase'))")" = "rolled-back" ] && python3 tools/pair_report.py passage2-test --post "#27 passage (queen excluded)" > data/online/smoke/passage2-report.log 2>&1
