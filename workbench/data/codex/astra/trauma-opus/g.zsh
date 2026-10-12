#!/bin/zsh
# g.zsh <arm> <botA> <botB> <map path> <side>
arm=$1; A=$2; B=$3; map=$4; side=$5
R=~/meow-redteam
mn=${map:t:r}
out=$R/solo/runs/tr_$arm/$mn-seed${SEED:-1}-side$side
rm -f $out/stdout.txt
mkdir -p $out
if [[ $side == 0 ]]; then
  $R/play.sh $R/solo/bots/$A $R/solo/bots/$B $map ${SEED:-1} $out > $out.log 2>&1
else
  $R/play.sh $R/solo/bots/$B $R/solo/bots/$A $map ${SEED:-1} $out > $out.log 2>&1
fi
echo done $arm $mn $side
