#!/bin/zsh
# Codex analyst (Astra, a thinking job): the two 1-4 battles against Team SKKU.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
mkdir -p data/codex/astra/skku
nohup tools/cx.sh data/codex/astra-skku.log -m gpt-6-astra -c model_reasoning_effort=high -s workspace-write -C "$PWD" "Follow the brief in data/codex/brief-astra-skku.md exactly." > /dev/null 2>&1 &
sleep 20
head -n 12 data/codex/astra-skku.log | grep -i "model\|limit\|error" | cut -c1-120
tail -n 2 data/codex/accounts.log
date "+%H:%M:%S"
