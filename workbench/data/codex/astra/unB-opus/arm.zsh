# usage: arm.zsh <par> <map> <side> <opp> bot...   games into runs/ub_a_<bot>/
par=$1; name=$2; side=$3; opp=$4; shift 4
cd ~/meow-redteam
n=0
for bot in "$@"; do
  mkdir -p solo/runs/ub_a_$bot
  out=solo/runs/ub_a_$bot/$name-seed7-side$side
  if [ -e $out/result.txt ]; then continue; fi
  if [ $side = 0 ]; then
    ./play.sh solo/bots/$bot solo/bots/$opp ${MAPDIR:-maps/un2}/$name.map 7 $out > $out.log 2>&1 &
  else
    ./play.sh solo/bots/$opp solo/bots/$bot ${MAPDIR:-maps/un2}/$name.map 7 $out > $out.log 2>&1 &
  fi
  n=$((n+1))
  if [ $((n % par)) = 0 ]; then wait; fi
done
wait
cd "~/01. Project/개인 프로젝트/unsw-swarm"
for bot in "$@"; do
  echo "== $bot"
  python3 -B data/codex/astra/unB-opus/health.py ub_a_$bot $name | cut -c1-200
done
date
