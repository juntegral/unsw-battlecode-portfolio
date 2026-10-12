#!/bin/zsh
# qmate-opus: wait until run.log has $1 lines or $2 seconds pass.
L="~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/qmate-opus/run.log"
t=0
until [ $(wc -l < "$L") -ge $1 ] || [ $t -ge $2 ]; do sleep 5; t=$((t+5)); done
cat "$L"; date
