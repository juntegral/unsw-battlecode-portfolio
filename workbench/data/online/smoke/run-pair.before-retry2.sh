#!/bin/zsh
# usage: run-pair.sh <label> <botdir> <card ref text> [opponent ids, default 19,87,545]
# Plays the NEW bot only (15 maps per opponent) and compares it with the pooled live baseline.
# BASELINE=1 also replays the live bot first (use at most 2 opponents: 60 games an hour per allowance).
# 19 test4, 87 WeHaveQuizzes (normal allowance); 545 dev1 (DEV allowance, catches our queen).
cd "~/01. Project/개인 프로젝트/unsw-swarm"
LABEL="$1"; BOT="$2"; REF="$3"; OPP="${4:-19,87,545}"
M=28,29,30,31,32,33,34,4,7,9,11,13,15,20,21
N=$(echo "$OPP" | tr ',' '\n' | wc -l | tr -d ' ')
NAMES=$(echo "$OPP" | sed -e 's/545/dev1/' -e 's/87/WeHaveQuizzes/' -e 's/19/test4/' -e 's/,/ + /g')
if [ "${BASELINE:-0}" = 1 ]; then MODE=(--games $((30 * N))); WHAT="live bot, then live + $REF, 15 maps each vs $NAMES"
else MODE=(--new-only --games $((15 * N))); WHAT="live + $REF, 15 maps vs each of $NAMES, compared with the live bot's earlier games"; fi
BASEID=$(node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}')
say() { printf '%s\n' "$1" > data/guide/px-$LABEL.txt; python3 tools/meowbot.py --announce-file data/guide/px-$LABEL.txt; }
started=0
for i in $(seq 1 70); do
  rm -f data/online/smoke/$LABEL.json
  python3 tools/smoke.py pair "$BOT" --name $LABEL --opp $OPP --maps $M $MODE --confirm > data/online/smoke/$LABEL.log 2>&1 &
  pid=$!
  sleep 25
  if kill -0 $pid 2>/dev/null; then started=1; break; fi
  # wait and retry when battles are live or the hourly allowance is not back yet
  grep -q "refusing to swap or start\|Insufficient\|live or pending" data/online/smoke/$LABEL.log || break
  sleep 30
done
if [ $started = 0 ]; then
  say "couldn't start the $REF online test ($(tail -1 data/online/smoke/$LABEL.log | cut -c1-150)). the live bot is unchanged. will retry later"
  exit 0
fi
say "🧪 testing online now: $WHAT. the active bot swaps for ~20 min, please don't upload or swap until \"done, swapped back\""
wait $pid
phase=$(python3 -c "import json;print(json.load(open('data/online/smoke/$LABEL.json')).get('phase'))" 2>/dev/null)
active=$(node tools/submit.js active 2>&1 | tail -1)
if ! echo "$active" | grep -q "^$BASEID "; then
  # the swap back did not happen: keep trying until other teams' battles are over
  for i in $(seq 1 40); do
    python3 tools/smoke.py rollback $LABEL --confirm >> data/online/smoke/$LABEL.log 2>&1 && break
    sleep 30
  done
  active=$(node tools/submit.js active 2>&1 | tail -1)
  played=$(python3 -c "import json;h=json.load(open('data/online/smoke/$LABEL.json'))['halves']['new'];print(int(h.get('phase')=='finished'))" 2>/dev/null)
  [ "$played" = 1 ] && echo "$active" | grep -q "^$BASEID " && phase=rolled-back
fi
if echo "$active" | grep -q "^$BASEID " && [ "$phase" = "rolled-back" ]; then
  say "✅ done, swapped back: the live bot is active again. $REF comparison finished, results coming on the card"
elif echo "$active" | grep -q "^$BASEID "; then
  say "⚠️ $REF online test stopped early (phase: $phase). the live bot is active, nothing is broken. checking what happened"
else
  say "⚠️ $REF online test ended and the live bot was NOT restored (active: $active). please don't upload; run: node tools/submit.js activate $BASEID --confirm"
fi
touch data/online/smoke/$LABEL-finished
