#!/bin/zsh
# usage: run-pair.sh <label> <botdir> <card ref text> ; base = the currently active submission
cd "~/01. Project/개인 프로젝트/unsw-swarm"
LABEL="$1"; BOT="$2"; REF="$3"
M=28,29,30,31,32,33,34,4,7,9,11,13,15,20,21
BASEID=$(node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}')
say() { printf '%s\n' "$1" > data/guide/px-$LABEL.txt; python3 tools/meowbot.py --announce-file data/guide/px-$LABEL.txt; }
started=0
for i in $(seq 1 60); do
  rm -f data/online/smoke/$LABEL.json
  python3 tools/smoke.py pair "$BOT" --name $LABEL --opp 19,87 --maps $M --confirm > data/online/smoke/$LABEL.log 2>&1 &
  pid=$!
  sleep 25
  if kill -0 $pid 2>/dev/null; then started=1; break; fi
  grep -q "refusing to swap or start" data/online/smoke/$LABEL.log || break
  sleep 30
done
if [ $started = 0 ]; then
  say "couldn't start the $REF online test ($(tail -1 data/online/smoke/$LABEL.log | cut -c1-150)). the live bot is unchanged. will retry later"
  exit 0
fi
say "🧪 testing online now: live bot vs live + $REF, 30 games each vs test4 + WeHaveQuizzes, same 15 maps. the active bot swaps for ~30 min, please don't upload or swap until \"done, swapped back\""
wait $pid
phase=$(python3 -c "import json;print(json.load(open('data/online/smoke/$LABEL.json')).get('phase'))" 2>/dev/null)
active=$(node tools/submit.js active 2>&1 | tail -1)
if echo "$active" | grep -q "^$BASEID " && [ "$phase" = "rolled-back" ]; then
  say "✅ done, swapped back: the live bot is active again. $REF comparison finished, results coming on the card"
elif echo "$active" | grep -q "^$BASEID "; then
  say "⚠️ $REF online test stopped early (phase: $phase). the live bot is active, nothing is broken. checking what happened"
else
  say "⚠️ $REF online test ended and the live bot was NOT restored (active: $active). please don't upload; run: node tools/submit.js activate $BASEID --confirm"
fi
touch data/online/smoke/$LABEL-finished
