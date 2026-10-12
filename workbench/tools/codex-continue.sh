#!/bin/zsh
# Continue the unsw-swarm work with Codex when Claude is unavailable (user request 2026-10-01).
# usage: tools/codex-continue.sh [task-id like W2] ["extra instruction"]
# Runs gpt-6.1-sol (effort high) in this repository with workspace write access; network stays off (no uploads).
# The final upload (AGENTS.md section 5) needs network: run the printed submit command yourself.
REPO="$(cd "$(dirname "$0")/.." && pwd)"
TASK="${1:-the first task whose status is 열림 (open)}"
EXTRA="${2:-}"
STAMP=$(date +%Y%m%d-%H%M%S)
LOG="$REPO/exp/codex-runs/$STAMP.log"; LAST="$REPO/exp/codex-runs/$STAMP-last.txt"
PROMPT="You are continuing the unsw-swarm project. First read AGENTS.md and docs/WORKQUEUE.md completely, then the files they point to for your task.
Take task: $TASK. Mark it '진행 중(Codex, <real time from date>)' in docs/WORKQUEUE.md before starting.
Follow AGENTS.md section 2 (rules) and section 4 (diagram-first, pre-registration, identity checks, unseen-map measurement) exactly.
Do not request online battles and do not upload. Keep at most 3 local games of your own and never exceed 6 machine-wide (pgrep -f \"unswbc-clean.py run\" | wc -l); stop new games below 21 GB free disk.
When done or when you must stop: update docs/WORKQUEUE.md status, add a dated line (real clock) to DECISIONS.md, commit your paths with git -c user.name=juntegral -c user.email=<email>, and end with a short Korean summary for the user.
$EXTRA"
echo "$(date +%H:%M:%S) start task=$TASK log=$LOG"
cd "$REPO" && nice -n 10 codex exec -m gpt-6.1-sol -c 'model_reasoning_effort="high"' -C "$REPO" -s workspace-write --skip-git-repo-check -o "$LAST" "$PROMPT" > "$LOG" 2>&1
echo "$(date +%H:%M:%S) exit $? (summary: $LAST)"
