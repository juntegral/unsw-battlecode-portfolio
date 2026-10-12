cd "~/01. Project/개인 프로젝트/unsw-swarm"
python3 -B data/codex/astra/qbox-opus/tab.py qb_off_b qb_pa_b qb_r2_b qb_off_d qb_pa_d qb_r2_d 2>&1 | sort -k2,2 -k1,1 -s > data/codex/astra/qbox-opus/table.txt
cat data/codex/astra/qbox-opus/table.txt
echo == identical replays
cd ~/meow-redteam/solo/runs
for o in b d; do
for d in qb_off_$o/*; do
  g=${d:t}
  [[ -f $d/result.txt ]] || continue
  for a in pa r2; do
    f=qb_${a}_$o/$g/game.replay
    [[ -f qb_${a}_$o/$g/result.txt ]] || continue
    if cmp -s $d/game.replay $f; then echo "$o $g $a SAME"; else echo "$o $g $a differs"; fi
  done
done
done
