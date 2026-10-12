#!/bin/zsh
# exits when the count of one15 games on disk grows beyond $1 (or after ~25 min)
cd "~/01. Project/개인 프로젝트/unsw-swarm"
n0=$1
for i in {1..50}; do
  n=$(python3 -B data/codex/astra/loss15-sonnet/list15.py | wc -l)
  if [ "$n" -gt "$n0" ]; then echo "now $n"; exit 0; fi
  sleep 30
done
echo "timeout $n"
