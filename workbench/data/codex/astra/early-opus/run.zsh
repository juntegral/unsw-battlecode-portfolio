# usage: run.zsh <arm> <bot> <opp> <seed> <side> <map path> [<map path> ...]   (2 games at a time)
arm=$1; bot=$2; opp=$3; seed=$4; side=$5; shift 5
cd ~/meow-redteam
n=0
for m in "$@"; do
  name=$(basename $m .map)
  out=solo/runs/ea_$arm/$name-seed$seed-side$side
  if [ -f $out/result.txt ]; then continue; fi
  mkdir -p solo/runs/ea_$arm
  if [ $side = 0 ]; then
    ./play.sh solo/bots/$bot solo/bots/$opp $m $seed $out > $out.log 2>&1 &
  else
    ./play.sh solo/bots/$opp solo/bots/$bot $m $seed $out > $out.log 2>&1 &
  fi
  n=$((n+1))
  if [ $((n%2)) = 0 ]; then wait; fi
done
wait
echo done $arm
