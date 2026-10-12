#!/bin/zsh
U="~/01. Project/개인 프로젝트/unsw-swarm"; T="$U/data/analysis/top1"; D="$U/data/codex"
B="~/01. Project/개인 프로젝트/battlecode"
cd "$U"
log() { echo "$(date '+%m-%d %H:%M:%S') $*" >> "$T/study.log"; }
log "phase 1: metrics script (codex)"
codex exec -m gpt-6-astra -c model_reasoning_effort=high -s workspace-write -C . --add-dir "$B" -o "$D/last-top-metrics.txt" "Follow the brief in data/codex/brief-top-metrics.md exactly." < /dev/null > "$D/run-top-metrics.log" 2>&1
log "phase 1 done: $(ls $T | tr '\n' ' ')"
# wait for more replays: until the collector stops (disk cap) or 01:30, whichever comes first
while pgrep -f "tools/top_collect.py" >/dev/null && [ "$(date +%Y%m%d%H%M)" -lt 202610050130 ]; do sleep 120; done
log "phase 2: study session starts with $(ls data/online/top1 | wc -l | tr -d ' ') battles"
cd "$T"
LOOP_GUARD="$B/work/loop/guard.py" CARD_LOOP_GUARD="$B/work/loop/guard.py" LOOP_TREE="$T" LOOP_OUT="$T" LOOP_STEP=study CARD_LOOP_GAMES=0 LOOP_BATCH_LEASE=0 \
  claude -p --model opus --effort high --permission-mode bypassPermissions --settings "$B/work/loop/settings.json" --output-format stream-json --verbose < "$T/STUDY-PROMPT.md" > "$T/study.jsonl" 2>&1
log "study session ended; DONE=$([ -f $T/DONE ] && echo yes || echo no)"
