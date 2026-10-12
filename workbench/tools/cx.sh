#!/bin/zsh
# Codex with account fallback: the Plus account (Orca-managed home) first; if it reports a usage/rate limit,
# run the same command again with the default ~/.codex account.
# usage: tools/cx.sh <log file> <codex exec args...>      (stdin is closed; output goes to the log file)
LOG="$1"; shift
PLUS="$HOME/Library/Application Support/Orca/codex-accounts/910a88f2-d9b3-4ef1-b51a-b00a1b1a910e/home"
NOTE="$(dirname "$0")/../data/codex/accounts.log"
limited() { [ "${rc:-1}" -ne 0 ] && tail -n 60 "$LOG" | grep -qiE "usage limit|hit your .*limit|rate limit|quota|too many requests|\b429\b"; }
if [ -f "$PLUS/auth.json" ] && [ ! -f "$PLUS/.limit-until" -o "$(cat "$PLUS/.limit-until" 2>/dev/null || echo 0)" -lt "$(date +%s)" ]; then
  CODEX_HOME="$PLUS" codex exec "$@" < /dev/null > "$LOG" 2>&1; rc=$?
  if ! limited; then echo "$(date '+%m-%d %H:%M') plus rc=$rc $(basename "$LOG")" >> "$NOTE"; exit $rc; fi
  # remember the limit for 3 hours so later calls skip straight to the second account
  echo $(( $(date +%s) + 10800 )) > "$PLUS/.limit-until"
  echo "$(date '+%m-%d %H:%M') plus hit its limit, falling back: $(basename "$LOG")" >> "$NOTE"
  mv "$LOG" "$LOG.plus-limit"
fi
CODEX_HOME="$HOME/.codex" codex exec "$@" < /dev/null > "$LOG" 2>&1; rc=$?
echo "$(date '+%m-%d %H:%M') second account rc=$rc $(basename "$LOG")" >> "$NOTE"
exit $rc
