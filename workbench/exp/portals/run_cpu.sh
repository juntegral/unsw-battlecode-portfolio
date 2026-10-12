#!/bin/zsh
# exp/portals: CPU per turn (the judge's points) for a bot on Portals: the unswbc summary lines of N sandboxed games
# usage: exp/portals/run_cpu.sh <botDir> <label> <seeds...>   (both sides against proxy4_king, one game at a time, nice 10)
cd "$(dirname "$0")/../.."
B=$1; L=$2; shift 2
mkdir -p exp/portals/cpu/$L
for s in "$@"; do for side in A B; do
  d=exp/portals/cpu/$L/$side$s; mkdir -p $d
  if [ $side = A ]; then a=$B; b=bots/proxy4_king; else a=bots/proxy4_king; b=$B; fi
  nice -n 10 tools/unswbc run exp/portals/maps-portals/portals.map $a $b --sandbox --seed $s --no-logs --no-draw -o $d/game.replay > $d/out.txt 2>&1
  grep "team $side points" $d/out.txt >> exp/portals/cpu/$L/points.txt
done; done
