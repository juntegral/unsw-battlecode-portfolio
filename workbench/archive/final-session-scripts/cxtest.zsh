#!/bin/zsh
# After the user's Codex reset: clear the 3-hour skip marker of the first account and run one tiny job on each account.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
PLUS="$HOME/Library/Application Support/Orca/codex-accounts/910a88f2-d9b3-4ef1-b51a-b00a1b1a910e/home"
[ -f "$PLUS/.limit-until" ] && echo "marker was $(cat "$PLUS/.limit-until"), removed" && rm "$PLUS/.limit-until"
T=~/.claude/jobs/e2109d93/tmp
CODEX_HOME="$PLUS" codex exec -m gpt-6.1-sol -s read-only "Reply with the single word ok." < /dev/null > $T/cx-plus.log 2>&1
echo "first account rc=$? | $(tail -n 3 $T/cx-plus.log | tr '\n' ' ' | cut -c1-200)"
CODEX_HOME="$HOME/.codex" codex exec -m gpt-6.1-sol -s read-only "Reply with the single word ok." < /dev/null > $T/cx-second.log 2>&1
echo "second account rc=$? | $(tail -n 3 $T/cx-second.log | tr '\n' ' ' | cut -c1-200)"
date "+%H:%M:%S"
