#!/bin/zsh
# Every 5 minutes: start the synthesis of any round whose reports are in; start a round when an online test queue of the live
# bot has finished (one round a bot generation) OR as soon as a ranked game has been lost (jun, 04:4x: react to every loss).
# Each game line names the version that played it. Stops at 2026-10-09 14:30 KST. Log: data/codex/astra/sweep/loop.log
cd "$(dirname "$0")/.." || exit 1
END=$(date -j -f "%Y-%m-%d %H:%M" "2026-10-09 14:30" +%s)
LAST=$(grep -c "queue runner done" data/online/smoke/at-q.log 2>/dev/null)
while [ $(date +%s) -lt $END ]; do
  sleep 300
  python3 tools/sweep_games.py --synth >> data/codex/astra/sweep/loop.log 2>&1
  NOW=$(grep -c "queue runner done" data/online/smoke/at-q.log 2>/dev/null)
  LOST=$(python3 tools/sweep_games.py --pending 2>/dev/null | cut -d' ' -f1)
  if [ "$NOW" -gt "$LAST" ] || [ "${LOST:-0}" -gt 0 ]; then
    LAST=$NOW
    echo "$(date '+%H:%M:%S') round (queue done $NOW, new ranked losses ${LOST:-0})" >> data/codex/astra/sweep/loop.log
    python3 tools/sweep_games.py --round >> data/codex/astra/sweep/loop.log 2>&1
  fi
done
