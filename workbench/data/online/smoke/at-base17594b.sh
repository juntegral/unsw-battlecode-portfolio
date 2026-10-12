#!/bin/zsh
# More live-bot games for the 17594 baseline: uploads the same main as a test bot (new half only), then registers
# the games as baseline. Waits until 20:27 KST so the normal allowance is back.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
LOG=data/online/smoke/at-base17594b.log
log() { echo "$(date '+%F %T') $1" >> $LOG; }
phase() { python3 -c "import json;print(json.load(open('data/online/smoke/$1.json')).get('phase'))" 2>/dev/null || echo none; }
log "baseline top-up queued (pid $$)"
while [ "$(date +%H%M)" -lt 2027 ]; do sleep 30; done
if pgrep -f "run-pair[.]sh" > /dev/null; then log "another pair test is running; waiting"; while pgrep -f "run-pair[.]sh" > /dev/null; do sleep 30; done; fi
for f in main.cpp bot.toml helper.hpp sonar_codec.hpp; do cmp -s ~/meow-release/mybot2/$f data/online/smoke/qw37-bot/$f || { log "release folder is not the live bot any more ($f); stopping"; exit 1; }; done
node tools/submit.js check ~/meow-release/mybot2 2>&1 | tail -n 1 | grep -q "identical" || { log "active bot is not the release folder; stopping"; exit 1; }
log "starting bl17594b-test (the live bot again vs 19,87)"
data/online/smoke/run-pair.sh bl17594b-test ~/meow-release/mybot2 "live bot again (more baseline games)" 19,87
P=$(phase bl17594b-test); log "bl17594b-test ended; phase: $P"
if [ "$P" = "rolled-back" ]; then
  python3 - <<'PY' >> $LOG 2>&1
import json, os
os.chdir('data/online/smoke')
src, dst = 'bl17594b-test', 'base17594-test2'
d = json.load(open(src + '.json'))
h = dict(d['halves']['new']); h['submission'] = {'id': 17594, 'name': 'card-25-ff0327008d'}; h['label'] = dst
d['halves'] = {'old': h, 'new': {**d['halves']['old'], 'battle_ids': [], 'submission': None}}
d['label'] = dst; d['rollback'] = {'id': 17594, 'name': 'card-25-ff0327008d'}
d['note'] = 'Baseline alias: second run of the same four source files as submission 17594 (5 Oct evening).'
json.dump(d, open(dst + '.json', 'w'), indent=1)
if not os.path.exists(dst + '-old'): os.symlink(src + '-new', dst + '-old')
print('alias written', dst, len(h['battle_ids']))
PY
  python3 tools/pair_report.py bl17594b-test > data/online/smoke/bl17594b-report.log 2>&1
  log "report: $(head -n 1 data/online/smoke/bl17594b-test-result.txt | cut -c1-160)"
fi
log "active bot at end: $(node tools/submit.js active 2>&1 | tail -1 | awk '{print $1}')"
log "baseline top-up done"
