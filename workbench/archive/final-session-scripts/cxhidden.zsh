#!/bin/zsh
# Follow-up builder on Codex: hidden (assumed size for an enemy whose body leaves the view), on top of the seen builder's source.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
mkdir -p data/codex/build/hidden
cp data/codex/build/seen/main.cpp data/codex/build/hidden/main.cpp
cp data/codex/build/seen/main.base.cpp data/codex/build/hidden/main.base.cpp
cp data/codex/build/seen/one14.switches data/codex/build/hidden/one14.switches
nohup tools/cx.sh data/codex/build-hidden.log -m gpt-6-astra -c model_reasoning_effort=high -s workspace-write -C "$PWD" "Follow the brief in data/codex/brief-build-hidden.md exactly." > /dev/null 2>&1 &
sleep 5
pgrep -f "codex exec -m" | wc -l
date "+%H:%M:%S"
