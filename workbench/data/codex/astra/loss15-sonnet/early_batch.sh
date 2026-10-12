#!/bin/zsh
# usage: early_batch.sh <R> <step> <ids...>   (writes to early-out.txt)
cd "~/01. Project/개인 프로젝트/unsw-swarm"
R=$1; S=$2; shift; shift
for g in "$@"; do
  echo "== $g"
  python3 -B data/codex/astra/loss15-sonnet/early.py $g $R $S 2>&1 | cut -c1-240
done > data/codex/astra/loss15-sonnet/early-out.txt
