# usage: run.zsh <opp> <seed> <side> <map path> <arm=bot> [<arm=bot> ...]   (all at once, give at most 4)
opp=$1; seed=$2; side=$3; m=$4; shift 4
cd ~/meow-redteam
name=$(basename $m .map)
for ab in "$@"; do
  arm=${ab%%=*}; bot=${ab##*=}
  out=solo/runs/ty_$arm/$name-seed$seed-side$side
  if [ -e $out ]; then continue; fi
  mkdir -p solo/runs/ty_$arm
  if [ $side = 0 ]; then
    ./play.sh solo/bots/$bot solo/bots/$opp $m $seed $out > $out.log 2>&1 &
  else
    ./play.sh solo/bots/$opp solo/bots/$bot $m $seed $out > $out.log 2>&1 &
  fi
done
wait
echo run done $name $seed $side "$@"
