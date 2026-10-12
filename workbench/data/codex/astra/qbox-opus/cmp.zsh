date
cd ~/meow-redteam/solo/runs
for o in b d; do
  for d in qb_off_$o/*; do
    g=${d:t}
    [[ -f $d/result.txt ]] || continue
    for a in nb pa; do
      [[ -f qb_${a}_$o/$g/result.txt ]] || continue
      if cmp -s $d/game.replay qb_${a}_$o/$g/game.replay; then echo "$a $o $g SAME"; else echo "$a $o $g differs"; fi
    done
  done
done
