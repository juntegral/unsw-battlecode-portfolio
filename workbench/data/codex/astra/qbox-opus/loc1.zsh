cd "~/01. Project/개인 프로젝트/unsw-swarm"
Q=data/codex/astra/qbox-opus/qd.py
for arm in lc_mTd0 lc_mNps pc_mNps; do
  for d in ~/meow-redteam/solo/runs/$arm/ladder_portals_1-*; do
    k=${d##*side}
    echo "== $arm ${d:t}"; cat $d/result.txt | head -3
    python3 -B $Q $d/game.replay $k 3 brief
  done
done
