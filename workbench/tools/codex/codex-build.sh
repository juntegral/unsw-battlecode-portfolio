#!/bin/zsh
# usage: codex-build.sh <task-slug> "<task line>"   (build phase only; no games)
S="${CODEX_LOGS:-$HOME/.cache/unsw-codex}"; mkdir -p "$S"
R="~/01. Project/개인 프로젝트/unsw-swarm"
echo "$(date +%H:%M:%S) start $1" >> $S/codex-build-runner.log
cd "$R" && nice -n 10 codex exec -m gpt-6.1-sol -c 'model_reasoning_effort="high"' -C "$R" -s workspace-write --skip-git-repo-check -o $S/codex-build-$1-last.txt "TASK: $2 (task slug for paths: $1)

$(cat "$R/research/briefs/codex-build-template.md")" < /dev/null > $S/codex-build-$1.log 2>&1
echo "$(date +%H:%M:%S) exit $? $1" >> $S/codex-build-runner.log
