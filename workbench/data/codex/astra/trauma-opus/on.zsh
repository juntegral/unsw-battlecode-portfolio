#!/bin/zsh
cd "~/01. Project/개인 프로젝트/unsw-swarm"
for p in one15-p1-old/M1525842 one15-s1-old/M1527409 one16-c1-old/M1528866; do
  echo "=== $p"
  python3 -B data/codex/astra/trauma-opus/tr.py data/online/smoke/$p.replay 0 0 100 5 2>&1 | grep "us \|side 0\|^jumps\|^eats" | cut -c1-420
done
