#!/bin/zsh
cd "~/01. Project/개인 프로젝트/unsw-swarm"
sleep 20
while pgrep -f "smoke.py pair .*passage-test" >/dev/null; do sleep 30; done
phase=$(python3 -c "import json;print(json.load(open('data/online/smoke/passage-test.json')).get('phase'))")
if node tools/submit.js active 2>&1 | grep -q "16577"; then
  if [ "$phase" = "failed" ]; then
    printf '⚠️ #27 online test stopped early (%s). the live bot (stride, 16577) is active, nothing is broken. checking what happened\n' "$(tail -3 data/online/smoke/passage-test.log | tr '\n' ' ' | cut -c1-200)" > data/guide/b2.txt
  else
    printf '✅ done, swapped back: the live bot (stride) is active again. #27 comparison finished, results coming on the card\n' > data/guide/b2.txt
  fi
else
  printf '⚠️ #27 online test ended and the live bot was NOT restored automatically. please don'"'"'t upload; run: node tools/submit.js activate 16577 --confirm\n' > data/guide/b2.txt
fi
python3 tools/meowbot.py --announce-file data/guide/b2.txt
python3 tools/smoke.py report passage-test > data/online/smoke/passage-test-report.log 2>&1
touch data/online/smoke/passage-finished
