# usage: chain.zsh <opp> <seed> <side> "<arm=bot> ..." <map> [<map> ...]   (map-major order, 3 games at a time)
opp=$1; seed=$2; side=$3; arms=(${=4}); shift 4
cd ~/meow-redteam
n=0
for m in "$@"; do
  name=$(basename $m .map)
  for ab in $arms; do
    arm=${ab%%=*}; bot=${ab##*=}
    out=solo/runs/ea_$arm/$name-seed$seed-side$side
    if [ -e $out ]; then continue; fi
    mkdir -p solo/runs/ea_$arm
    if [ $side = 0 ]; then
      ./play.sh solo/bots/$bot solo/bots/$opp $m $seed $out > $out.log 2>&1 &
    else
      ./play.sh solo/bots/$opp solo/bots/$bot $m $seed $out > $out.log 2>&1 &
    fi
    n=$((n+1))
    if [ $((n%3)) = 0 ]; then wait; fi
  done
done
wait
echo chain done
