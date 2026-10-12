#!/bin/zsh
# Codex state: limit markers of both accounts, running jobs, the newest briefs, the sweep ledger tail.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
date "+%H:%M:%S"
grep -n "limit-until\|CODEX_HOME=" tools/cx.sh | cut -c1-160
for h in "$HOME/.codex" "$HOME/.codex-juntegral" "$HOME/.codex-plus"; do
  [ -d "$h" ] && echo "$h: $(ls -a "$h" | grep -c limit-until) marker(s) $(cat "$h/.limit-until" 2>/dev/null)"
done
pgrep -fl "codex exec" | cut -c1-120 | head -5
ls -t data/codex/ | grep "^brief-" | head -12
ls data/codex/astra/sweep/ | tail -5
tail -n 3 data/codex/astra/sweep/ledger.txt | cut -c1-120
