# usage: run.zsh <arm> <botA> <botB> <side> map...   three at a time
arm=$1; A=$2; B=$3; side=$4; shift 4
cd ~/meow-redteam
mkdir -p solo/runs/$arm
n=0
for name in "$@"; do
  out=solo/runs/$arm/$name-seed7-side$side
  if [ -e $out/result.txt ]; then continue; fi
  ./play.sh solo/bots/$A solo/bots/$B maps/un2/$name.map 7 $out > $out.log 2>&1 &
  n=$((n+1))
  if [ $((n % 3)) = 0 ]; then wait; fi
done
wait
echo done $arm $(date +%H:%M:%S)
