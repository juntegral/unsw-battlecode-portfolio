date
cd ~/meow-redteam/solo/runs
echo running:
ps -axo pid,etime,command | grep "run_game.py" | grep "solo/runs/qb_" | grep -v grep | awk '{print $1, $2, $NF}' | sed 's#~/meow-redteam/solo/runs/##'
echo unfinished dirs:
for d in qb_*/*; do [[ -f $d/result.txt ]] || echo $d; done
echo finished: $(ls qb_*/*/result.txt | wc -l)
