#!/bin/zsh
# usage: batch.sh <out file> <ids...>
cd "~/01. Project/개인 프로젝트/unsw-swarm"
out=$1; shift
python3 -B data/codex/astra/loss15-sonnet/l15.py "$@" > "$out" 2>&1
