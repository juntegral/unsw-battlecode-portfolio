#!/bin/zsh
# usage: poll.sh <known battle ids, space separated>  : exits when a ranked battle folder not in the list holds 5 replays, or at 14:54 KST
cd "~/01. Project/개인 프로젝트/unsw-swarm"
known=" $(tr '\n' ' ' < data/codex/astra/battle-opus/known.txt) "
while true; do
  for d in data/online/live-one1/b*; do
    b=${d:t}
    [[ "$known" == *" $b "* ]] && continue
    n=$(ls $d/M*.replay 2>/dev/null | wc -l)
    g=$(ls $d/game-*.json 2>/dev/null | wc -l)
    if [[ $n -ge 1 && $n -eq $g && $g -le 6 ]]; then
      sleep 20
      echo "NEW $b replays $n"; date; exit 0
    fi
  done
  [[ $(date +%H%M) -ge 1454 ]] && { echo "TIME 14:54"; exit 0; }
  sleep 30
done
