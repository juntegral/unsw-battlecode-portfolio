#!/bin/zsh
# usage: run-pair.sh <label> <botdir> <card ref text> [opponent ids, default 19,87,545]
# Plays the NEW bot only (15 maps per opponent) and compares it with the pooled live baseline.
# LIVE_ONLY=1 plays only the live bot, with no upload or swap (botdir may be -).
# BASELINE=1 also replays the live bot first (use at most 2 opponents: 60 games an hour per allowance).
# 19 test4, 87 WeHaveQuizzes (normal allowance); 545 dev1 (DEV allowance, catches our queen).
cd "~/01. Project/개인 프로젝트/unsw-swarm"
LABEL="$1"; BOT="$2"; REF="$3"; OPP="${4:-19,87,545}"
M=28,29,30,31,32,33,34,4,7,9,11,13,15,20,21
N=$(echo "$OPP" | tr ',' '\n' | wc -l | tr -d ' ')
NAMES=$(echo "$OPP" | sed -e 's/946/Big Bobs Bots/' -e 's/545/dev1/' -e 's/87/WeHaveQuizzes/' -e 's/19/test4/' -e 's/,/ + /g')
if [ "${LIVE_ONLY:-0}" = 1 ]; then MODE=(--old-only --games $((15 * N))); WHAT="more live bot games for the baseline: 15 maps vs each of $NAMES. no bot swap, uploads are fine meanwhile"
elif [ "${BASELINE:-0}" = 1 ]; then MODE=(--games $((30 * N))); WHAT="live bot, then live + $REF, 15 maps each vs $NAMES"
else MODE=(--new-only --games $((15 * N))); WHAT="live + $REF, 15 maps vs each of $NAMES, compared with the live bot's earlier games"; fi
BASEID=$(node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}')
say() { printf '%s\n' "$1" > data/guide/px-$LABEL.txt; python3 tools/meowbot.py --announce-file data/guide/px-$LABEL.txt; }
bot_names() {
  python3 - "$LABEL" "$REF" "$1" "$NAMES" <<'PY_NAMES'
import json
from pathlib import Path
import sys
label, ref, notice, names = sys.argv[1:]
try:
    st = json.loads((Path('data/online/smoke') / (label + '.json')).read_text())
except (OSError, ValueError):
    st = {}
halves = st.get('halves', {})
new = (halves.get('new', {}).get('submission') or {}).get('version')
live = (halves.get('old', {}).get('submission') or {}).get('version')
main = f'v{live} main' if live is not None else 'live bot'
if notice == 'live':
    print(f'more {main} games for the baseline: 15 maps vs each of {names}. no bot swap, uploads are fine meanwhile')
elif notice == 'start':
    print(f'new bot = {main} + {ref}, 15 maps vs each of {names}')
elif new is not None and live is not None:
    print(f'✅ done, swapped back: {main} is active again. v{new} ({ref}) finished, result coming')
else:
    print(f'✅ done, swapped back: the live bot is active again. {ref} comparison finished, results coming on the card')
PY_NAMES
}
# Only a verified, unplayed upload failure may be archived for a fresh pair.
retry_state() {
  python3 - "$LABEL" "$BASEID" "${1:-check}" <<'PY_STATE'
import json
import os
from pathlib import Path
import re
import sys

label, baseid, action = sys.argv[1:]
path = Path('data/online/smoke') / (label + '.json')
try:
    state = json.loads(path.read_text())
    halves = state['halves']
    error = state.get('error', '')
    safe = (state.get('kind') == 'pair' and state.get('label') == label
            and state.get('phase') == 'failed'
            and state.get('active_verified') is True
            and state.get('rollback_required') is False
            and str(state['active_submission']['id']) == baseid
            and str(state['rollback']['id']) == baseid
            and set(halves) == {'old', 'new'}
            and halves['new'].get('submission') is None
            and str(halves['old']['submission']['id']) == baseid
            and all(h.get('battle_ids') == [] and h.get('requests') == []
                    and h.get('phase') in (None, 'skipped') for h in halves.values())
            and re.search(r'submit\.js upload failed.*(?:fetch failed|ECONNRESET|ETIMEDOUT|EAI_AGAIN|socket hang up)',
                          error, re.I | re.S))
    if not safe:
        sys.exit(1)
    if action == 'archive':
        n = 1
        while True:
            target = path.with_name(f'{label}.failed-{n}.json')
            try:
                os.link(path, target)
                break
            except FileExistsError:
                n += 1
        path.unlink()
        print(f'Preserved failed state: {target}')
except (OSError, ValueError, KeyError, TypeError):
    sys.exit(1)
PY_STATE
}
start_ready() {
  python3 - "$LABEL" <<'PY_START'
import json
from pathlib import Path
import sys
try:
    state = json.loads((Path('data/online/smoke') / (sys.argv[1] + '.json')).read_text())
    ready = (state.get('phase') == 'uploading'
             or bool(state.get('halves', {}).get('new', {}).get('submission')))
    sys.exit(0 if ready else 1)
except (OSError, ValueError, TypeError):
    sys.exit(1)
PY_START
}
announce_start() {
  if [ "$announced" = 0 ] && start_ready; then
    say "🧪 testing online now: $(bot_names start). the active bot swaps for ~20 min, please don't upload or swap until \"done, swapped back\""
    announced=1
  fi
}
rollback_guard() {
  python3 - "$LABEL" "$BASEID" "$REF" "$active" <<'PY_GUARD'
import json
from pathlib import Path
import re
import sys
label, baseid, ref, active = sys.argv[1:]
path = Path('data/online/smoke') / (label + '.json')
try:
    match = re.match(r'^(\d+)\s+(.+?)\s+\(', active)
    if not match:
        raise ValueError('active submission identity is unreadable')
    activeid, name = match.groups()
    state = json.loads(path.read_text()) if path.exists() else {}
    if state.get('rollback_skipped_manual_switch'):
        sys.exit(3)
    test = state.get('halves', {}).get('new', {}).get('submission') or {}
    if activeid in (baseid, str(test.get('id'))):
        sys.exit(0)
    if not state:
        raise ValueError('run state is unavailable')
    state.update(rollback_required=False, rollback_skipped_manual_switch=True,
                 active_submission={'id': int(activeid), 'name': name}, active_verified=True,
                 note=f'active bot was changed by hand to {activeid} and the rollback was skipped')
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(state, indent=2) + '\n')
    temp.replace(path)
    print(f'⚠️ {ref} online test stopped: someone set the active bot to {activeid} {name} during the test. leaving it as it is, nothing was swapped back. the bot that was live before the test was {baseid}')
    sys.exit(3)
except (OSError, ValueError, TypeError, AttributeError) as exc:
    print(str(exc), file=sys.stderr)
    sys.exit(2)
PY_GUARD
}
check_rollback() {
  local notice guard_exit
  notice=$(rollback_guard)
  guard_exit=$?
  if [ $guard_exit = 3 ]; then
    [ -z "$notice" ] || say "$notice"
    touch data/online/smoke/$LABEL-finished
    exit 1
  fi
  # active bot or state unreadable: no rollback on this pass, the caller retries
  [ $guard_exit = 0 ] || return 2
  return 0
}
network_retries=0
refusal_deadline=0
announced=0
attempts=0
reason=""
while true; do
  # A previous safe failed attempt cannot be resumed by smoke.py pair.
  if [ $attempts = 0 ] && [ -e "data/online/smoke/$LABEL.json" ] && retry_state; then
    sleep 60
    if ! retry_state archive; then
      reason="the failed state could not be safely preserved for another attempt"
      break
    fi
    network_retries=1
  fi
  if [ $refusal_deadline -gt 0 ] && [ $SECONDS -ge $refusal_deadline ]; then
    reason="$refusal_reason"
    break
  fi
  attempts=$((attempts + 1))
  python3 tools/smoke.py pair "$BOT" --name $LABEL --opp $OPP --maps $M $MODE --ref "$REF" --confirm > data/online/smoke/$LABEL.log 2>&1 &
  pid=$!
  sleep 25
  if [ "${LIVE_ONLY:-0}" = 1 ] && [ $announced = 0 ]; then
    say "🧪 $(bot_names live)"
    announced=1
  fi
  if [ "${LIVE_ONLY:-0}" != 1 ]; then
    while kill -0 $pid 2>/dev/null; do
      announce_start
      sleep 5
    done
    announce_start
  fi
  wait $pid
  pair_exit=$?
  [ $pair_exit = 0 ] && break
  if retry_state; then
    if [ $network_retries -ge 5 ]; then
      reason="the upload request kept failing on the network after five retries"
      break
    fi
    sleep 60
    if ! retry_state archive; then
      reason="the failed state could not be safely preserved for another attempt"
      break
    fi
    network_retries=$((network_retries + 1))
    continue
  fi
  # Refusals before state creation are safe to retry even after the first 25 seconds.
  if [ ! -e "data/online/smoke/$LABEL.json" ] && grep -Eq "refusing to swap or start|Insufficient|live or pending" data/online/smoke/$LABEL.log; then
    [ $refusal_deadline = 0 ] && refusal_deadline=$((SECONDS + 1800))
    if grep -Eq "refusing to swap or start|live or pending" data/online/smoke/$LABEL.log; then
      refusal_reason="the server kept refusing the swap for 30 minutes because other battles of ours were running"
    else
      refusal_reason="the server kept refusing the run for 30 minutes because the game allowance was insufficient"
    fi
    if [ $SECONDS -ge $refusal_deadline ]; then
      reason="$refusal_reason"
      break
    fi
    sleep $((refusal_deadline - SECONDS < 60 ? refusal_deadline - SECONDS : 60))
    continue
  fi
  reason=$(python3 - "$LABEL" <<'PY_REASON'
import json
from pathlib import Path
import sys
path = Path('data/online/smoke') / (sys.argv[1] + '.json')
try:
    error = json.loads(path.read_text()).get('error')
except (OSError, ValueError):
    error = None
if not error:
    lines = path.with_suffix('.log').read_text().splitlines()
    error = next((line for line in reversed(lines) if line.strip()), 'the run exited without a recorded reason')
print(' '.join(str(error).split())[:300])
PY_REASON
)
  break
done
phase=$(python3 -c "import json;print(json.load(open('data/online/smoke/$LABEL.json')).get('phase'))" 2>/dev/null)
if [ "${LIVE_ONLY:-0}" = 1 ]; then
  if [ "$phase" = "rolled-back" ]; then
    python3 tools/pair_report.py "$LABEL" --post "$REF" >> data/online/smoke/$LABEL.log 2>&1
    report_exit=$?
    pair_exit=$report_exit
    [ $report_exit = 0 ] || say "⚠️ live bot baseline games finished; result reporting failed. no bot swap or upload was performed"
  else
    say "⚠️ live bot baseline run stopped: ${reason:-phase ${phase:-not recorded}}. no bot swap or upload was performed"
  fi
  touch data/online/smoke/$LABEL-finished
  exit $pair_exit
fi
active=$(node tools/submit.js active 2>&1 | tail -1)
check_rollback
if ! echo "$active" | grep -q "^$BASEID "; then
  # the swap back did not happen: keep trying until other teams' battles are over
  for i in $(seq 1 40); do
    [ $i = 1 ] || active=$(node tools/submit.js active 2>&1 | tail -1)
    check_rollback || { sleep 30; continue; }
    python3 tools/smoke.py rollback $LABEL --confirm >> data/online/smoke/$LABEL.log 2>&1 && break
    sleep 30
  done
  active=$(node tools/submit.js active 2>&1 | tail -1)
  check_rollback
  played=$(python3 -c "import json;h=json.load(open('data/online/smoke/$LABEL.json'))['halves']['new'];print(int(h.get('phase')=='finished'))" 2>/dev/null)
  [ "$played" = 1 ] && echo "$active" | grep -q "^$BASEID " && phase=rolled-back
fi
if echo "$active" | grep -q "^$BASEID " && [ "$phase" = "rolled-back" ]; then
  say "$(bot_names done)"
elif echo "$active" | grep -q "^$BASEID "; then
  say "⚠️ $REF online test stopped early: ${reason:-the run ended without a completed comparison (phase: ${phase:-not recorded})}. the live bot is active, nothing is broken. checking what happened"
else
  say "⚠️ $REF online test ended and the live bot was NOT restored (active: $active). please don't upload; run: node tools/submit.js activate $BASEID --confirm"
fi
touch data/online/smoke/$LABEL-finished
