#!/bin/zsh
# Codex builder (Astra, a thinking job): orbit, on top of the one15 candidate source.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
mkdir -p data/codex/build/orbit
cp ~/meow-redteam/solo/src/w-one15/main.cpp data/codex/build/orbit/main.cpp
cp ~/meow-redteam/solo/src/w-one15/main.cpp data/codex/build/orbit/main.base.cpp
cp data/codex/build/seen/one14.switches data/codex/build/orbit/one14.switches
nohup tools/cx.sh data/codex/build-orbit.log -m gpt-6-astra -c model_reasoning_effort=high -s workspace-write -C "$PWD" "Follow the brief in data/codex/brief-build-orbit.md exactly." > /dev/null 2>&1 &
sleep 5
pgrep -fl "codex exec -m" | cut -c1-40,150-230
date "+%H:%M:%S"
