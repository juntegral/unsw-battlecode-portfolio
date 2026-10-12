#!/bin/zsh
# Astra audit of the last bot's source diff and switch changes (code reading only).
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
mkdir -p data/codex/astra/audit-final19
nohup tools/cx.sh data/codex/astra-audit-final19.log -m gpt-6-astra -c model_reasoning_effort=high -s workspace-write -C "$PWD" "Follow the brief in data/codex/brief-astra-final19.md exactly." > /dev/null 2>&1 &
sleep 15
head -n 12 data/codex/astra-audit-final19.log | grep -i "model:\|limit" | cut -c1-80
date "+%H:%M:%S"
