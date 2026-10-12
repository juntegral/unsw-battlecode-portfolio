#!/bin/zsh
# After the Codex reset (second account works, first still limited): three Codex jobs and the per-generation sweep loop.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
PLUS="$HOME/Library/Application Support/Orca/codex-accounts/910a88f2-d9b3-4ef1-b51a-b00a1b1a910e/home"
echo $(( $(date +%s) + 18000 )) > "$PLUS/.limit-until"
T=~/.claude/jobs/e2109d93/tmp
sed 's/,PORTAL_SCOUT_MIN_LEN:4//' $T/one13.switches > $T/one14.switches
grep -c "PORTAL_SCOUT" $T/one14.switches
for b in seen qsnear; do
  mkdir -p data/codex/build/$b
  cp ~/meow-redteam/solo/src/solo/main.cpp data/codex/build/$b/main.cpp
  cp ~/meow-redteam/solo/src/solo/main.cpp data/codex/build/$b/main.base.cpp
  cp $T/one14.switches data/codex/build/$b/one14.switches
done
mkdir -p data/codex/astra/regress
nohup tools/cx.sh data/codex/sol-regress.log -m gpt-6.1-sol -c model_reasoning_effort=high -s workspace-write -C "$PWD" "Follow the brief in data/codex/brief-sol-regress.md exactly." > /dev/null 2>&1 &
nohup tools/cx.sh data/codex/build-seen.log -m gpt-6-astra -c model_reasoning_effort=high -s workspace-write -C "$PWD" "Follow the brief in data/codex/brief-build-seen.md exactly." > /dev/null 2>&1 &
nohup tools/cx.sh data/codex/build-qsnear.log -m gpt-6-astra -c model_reasoning_effort=high -s workspace-write -C "$PWD" "Follow the brief in data/codex/brief-build-qsnear.md exactly." > /dev/null 2>&1 &
nohup tools/sweep_loop.sh > /dev/null 2>&1 &
sleep 20
pgrep -f "codex exec -m" | wc -l
pgrep -fl "sweep_loop" | cut -c1-80
tail -n 3 data/codex/accounts.log
date "+%H:%M:%S"
