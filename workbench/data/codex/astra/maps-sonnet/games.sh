#!/bin/zsh
cd ~/meow-redteam
run() {
  s=$1
  mkdir -p solo/runs/mapcheck/$s
  ./play.sh solo/bots/mNps solo/bots/m3base maps/ladder/ladder_${s}_1.map 1 solo/runs/mapcheck/$s > solo/runs/mapcheck/$s.log 2>&1
  echo "$s exit $?"
}
run queen_of_spades & run trauma & wait
run trophy & run default & wait
run devil & run maze & wait
run weakhold
