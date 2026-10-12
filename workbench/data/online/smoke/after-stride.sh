#!/bin/zsh
cd "~/01. Project/개인 프로젝트/unsw-swarm"
while pgrep -f "smoke.py pair .*stride-test" >/dev/null; do sleep 30; done
active=$(node tools/submit.js active 2>&1 | tail -3)
phase=$(python3 -c "import json;print(json.load(open('data/online/smoke/stride-test.json')).get('phase'))")
if echo "$active" | grep -q "15011"; then
  printf '✅ done, swapped back: v61 is active again. stride vs v61 results (30 games each vs test4 + WeHaveQuizzes) are being written up, coming on #21\n' > data/guide/announce-pair-done.txt
else
  printf '⚠️ online test stopped early (phase: %s) and v61 may NOT be active. please don'"'"'t upload; 준싱 needs to run the rollback: node tools/submit.js activate 15011 --confirm\n' "$phase" > data/guide/announce-pair-done.txt
fi
python3 tools/meowbot.py --announce-file data/guide/announce-pair-done.txt
python3 tools/smoke.py report stride-test > data/online/smoke/stride-test-report.log 2>&1
