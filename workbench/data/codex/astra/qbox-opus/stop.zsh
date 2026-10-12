# stop my runner and all but the first 6 of my own games (matched by my runs/qb_ output folders and my runner as parent)
R=$(pgrep -f "qbox-opus/run.zsh .*jobs" | tr '\n' ' ')
echo runner $R
for r in ${=R}; do kill $r; done
n=0
ps -axo pid,command | grep "run_game.py" | grep "solo/runs/qb_" | grep -v grep | sort -n | while read pid rest; do
  n=$((n+1))
  if (( n > 6 )); then kill $pid; fi
done
sleep 1
ps -axo pid,command | grep "run_game.py" | grep "solo/runs/qb_" | grep -v grep | awk '{print $1, $NF}'
