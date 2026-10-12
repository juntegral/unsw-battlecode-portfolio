# usage: chain2.zsh <list file>   lines: <arm> <bot> <map path> <seed> <side>   (2 games at a time, opponent m3base)
cd ~/meow-redteam
n=0
while read arm bot m seed side; do
  [ -z "$arm" ] && continue
  name=$(basename $m .map)
  out=solo/runs/ty_$arm/$name-seed$seed-side$side
  if [ -e $out/result.txt ]; then continue; fi
  mkdir -p solo/runs/ty_$arm
  if [ -e $out ]; then continue; fi
  if [ $side = 0 ]; then
    ./play.sh solo/bots/$bot solo/bots/m3base $m $seed $out > $out.log 2>&1 &
  else
    ./play.sh solo/bots/m3base solo/bots/$bot $m $seed $out > $out.log 2>&1 &
  fi
  n=$((n+1))
  if [ $((n%2)) = 0 ]; then wait; fi
done < $1
wait
echo chain done $1
