#!/bin/zsh
# usage: wait_diag.sh name... : exits when the first of the named diagnoses has a result line, printing it
D="~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier"
while true; do
  for n in "$@"; do
    if tail -1 "$D/run-diag-$n.jsonl" 2>/dev/null | grep -q '"type":"result"'; then
      echo "=== $n done $(date '+%T')"
      tail -1 "$D/run-diag-$n.jsonl" | python3 -c "
import json,sys
d=json.loads(sys.stdin.read()); print(d.get('subtype'), 'min', round(d.get('duration_ms',0)/60000,1), 'usd', round(d.get('total_cost_usd',0),2)); print(str(d.get('result',''))[:3000])"
      exit 0
    fi
  done
  sleep 30
done
