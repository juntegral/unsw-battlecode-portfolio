#!/bin/zsh
# Last-hour sprint: start the crash check of the live build and three Codex (Astra) audits of the live source.
T=~/.claude/jobs/e2109d93/tmp
pgrep -f "tmp/stress17.zsh" > /dev/null || nohup zsh $T/stress17.zsh > /dev/null 2>&1 &
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
for a in audit-diff audit-time audit-unseen; do
  mkdir -p data/codex/astra/$a
  nohup tools/cx.sh data/codex/astra-$a.log -m gpt-6-astra -c model_reasoning_effort=high -s workspace-write -C "$PWD" "Follow the brief in data/codex/brief-astra-final-audit.md exactly. Your task is $a." > /dev/null 2>&1 &
done
sleep 20
for a in audit-diff audit-time audit-unseen; do echo "$a: $(head -n 12 data/codex/astra-$a.log | grep -i 'model:\|limit' | cut -c1-80)"; done
pgrep -f "codex exec -m" | wc -l
date "+%H:%M:%S"
