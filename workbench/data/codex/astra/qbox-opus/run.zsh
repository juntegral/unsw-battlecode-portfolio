# usage: run.zsh <jobfile>; lines: arm bot opp mapfile seed side ; at most 6 at a time
cd ~/meow-redteam
B=~/meow-redteam/solo/bots
LOG="~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/qbox-opus/logs"
mkdir -p $LOG
while read arm bot opp map seed side; do
  [[ -z "$arm" ]] && continue
  m=${map:t:r}
  out=~/meow-redteam/solo/runs/$arm/$m-seed$seed-side$side
  [[ -e $out ]] && continue
  mkdir -p ~/meow-redteam/solo/runs/$arm
  while (( $(jobs -r | wc -l) >= 6 )); do sleep 1; done
  if [[ $side == 0 ]]; then
    ./play.sh $B/$bot $B/$opp $map $seed $out > "$LOG/$arm-$m-$seed-$side.txt" 2>&1 &
  else
    ./play.sh $B/$opp $B/$bot $map $seed $out > "$LOG/$arm-$m-$seed-$side.txt" 2>&1 &
  fi
  sleep 0.3
done < $1
wait
echo done $1
