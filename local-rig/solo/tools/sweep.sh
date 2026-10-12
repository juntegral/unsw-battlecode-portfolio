#!/bin/zsh
# sweep.sh <arm>... : each arm plays m3base on the gx maps of 288 to 1536 cells, both sides, 6 games at a time.
cd ~/meow-redteam || exit 1
J=$(mktemp)
for m in $(awk -F'\t' 'NR>1 && $5>=288 && $5<=1536{print $1}' maps/gx/INDEX.tsv); do
  N=${m%.map}
  for a in "$@"; do
    for s in 0 1; do
      O=solo/runs/$a/$N-seed1-side$s
      [ -e $O/result.txt ] && continue
      if [ $s = 0 ]; then echo "./play.sh solo/bots/$a solo/bots/m3base maps/gx/$m 1 $O" >> $J
      else echo "./play.sh solo/bots/m3base solo/bots/$a maps/gx/$m 1 $O" >> $J; fi
    done
  done
done
wc -l < $J
xargs -P ${SWEEP_P:-6} -I{} sh -c '{} >> solo/runs/run.log 2>&1' < $J
echo "sweep-done $* $(date '+%T')" >> solo/runs/run.log
