#!/bin/zsh
# div.zsh <arm off> <arm on>: first differing trace line per shared game folder
cd "~/01. Project/개인 프로젝트/unsw-swarm"
T=~/.claude/jobs/e2109d93/tmp
R=~/meow-redteam/solo/runs
for d in $R/$2/*-side[01]; do
  n=${d:t}
  [[ -f $d/result.txt && -f $R/$1/$n/result.txt ]] || continue
  k=${n[-1]}
  python3 -B data/codex/astra/trauma-opus/tr.py $R/$1/$n/game.replay $k 0 500 1 > $T/div_a.txt 2>&1
  python3 -B data/codex/astra/trauma-opus/tr.py $d/game.replay $k 0 500 1 > $T/div_b.txt 2>&1
  if cmp -s $T/div_a.txt $T/div_b.txt; then echo "$n: traces identical"; else echo "$n: first difference: $(diff $T/div_a.txt $T/div_b.txt | grep '^[<>]' | head -2 | cut -c1-150 | tr '\n' '|')"; fi
done
