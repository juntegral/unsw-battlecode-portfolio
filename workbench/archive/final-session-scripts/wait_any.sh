#!/bin/zsh
# Returns when anything the main session is waiting for arrives: an online result, a Codex report or build, a round synthesis,
# a finished local batch, or a new desk-inbox line. Prints what is new.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
snap() { { ls data/online/smoke/*-result.txt data/codex/astra/*/report.md data/codex/build/*/done.txt data/codex/astra/sweep/*/synth/report.md 2>/dev/null; grep "done" ~/meow-redteam/solo/runs/run.log | sed 's/ [0-9:-]*$//' | sort -u; echo "inbox $(wc -c < data/guide/desk-inbox.txt)"; } | sort; }
A="$CLAUDE_JOB_DIR/tmp/wait_any.a"; B="$CLAUDE_JOB_DIR/tmp/wait_any.b"
snap > "$A"
while true; do
  sleep 30
  snap > "$B"
  if ! cmp -s "$A" "$B"; then date "+%H:%M:%S"; comm -13 "$A" "$B" | cut -c1-150; break; fi
done
