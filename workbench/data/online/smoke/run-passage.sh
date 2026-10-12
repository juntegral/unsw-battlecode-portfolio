#!/bin/zsh
cd "~/01. Project/개인 프로젝트/unsw-swarm"
BOT="~/01. Project/개인 프로젝트/battlecode/tune_runs/ab2/PASSAGE27"
M=28,29,30,31,32,33,34,4,7,9,11,13,15,20,21
say() { printf '%s\n' "$1" > data/guide/bx.txt; python3 tools/meowbot.py --announce-file data/guide/bx.txt; }
started=0
for i in $(seq 1 60); do
  rm -f data/online/smoke/passage-test.json
  python3 tools/smoke.py pair "$BOT" --name passage-test --opp 19,87 --maps $M --confirm > data/online/smoke/passage-test.log 2>&1 &
  pid=$!
  sleep 25
  if kill -0 $pid 2>/dev/null; then started=1; break; fi
  grep -q "refusing to swap or start" data/online/smoke/passage-test.log || break
  sleep 30
done
if [ $started = 0 ]; then
  say "couldn't start the #27 online test ($(tail -1 data/online/smoke/passage-test.log | cut -c1-150)). the live bot (stride) is unchanged. will retry later"
  exit 0
fi
say "🧪 #27 online test is running now for real (30 games each vs test4 + WeHaveQuizzes). please don't upload or swap until \"done, swapped back\""
wait $pid
phase=$(python3 -c "import json;print(json.load(open('data/online/smoke/passage-test.json')).get('phase'))" 2>/dev/null)
active=$(node tools/submit.js active 2>&1 | tail -1)
if echo "$active" | grep -q "16577" && [ "$phase" = "rolled-back" ]; then
  say "✅ done, swapped back: the live bot (stride) is active again. #27 comparison finished, results coming on the card"
elif echo "$active" | grep -q "16577"; then
  say "⚠️ #27 online test stopped early (phase: $phase). the live bot (stride) is active, nothing is broken. checking what happened"
else
  say "⚠️ #27 online test ended and the live bot was NOT restored (active: $active). please don't upload; run: node tools/submit.js activate 16577 --confirm"
fi
python3 tools/smoke.py report passage-test > data/online/smoke/passage-test-report.log 2>&1
touch data/online/smoke/passage-finished
