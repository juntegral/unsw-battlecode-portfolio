#!/bin/sh
# evalextra.sh: legality and queen/ring facts for runs/eval-final
cd "$(dirname "$0")/.."
err=$(grep -L '"bot_errors": \[\]' runs/eval-final/*/*/result.json 2>/dev/null | wc -l)
echo "games with bot runtime errors: $err"
nva=0; ring=0; n=0
for d in runs/eval-final/*/*/; do
  n=$((n+1))
  case "$d" in *side-0/) my=A; q=0;; *) my=B; q=1;; esac
  c=$(grep -c "team $my: no valid action" $d/engine.log); nva=$((nva+c))
  r=$(python3 mytools/queenpath.py $d/game.replay $q 2>/dev/null | head -1)
  case "$r" in *"stops from r None"*) ;; *"stops from r"*) ring=$((ring+1)); echo "RING $d $(echo "$r" | sed 's/.*queen/queen/') :: $(cat $d/result.txt | cut -c1-70)";; esac
done
echo "games=$n my 'no valid action' deaths=$nva games where the ring closed=$ring"
