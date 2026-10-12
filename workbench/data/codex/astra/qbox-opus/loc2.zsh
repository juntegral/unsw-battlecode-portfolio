cd "~/01. Project/개인 프로젝트/unsw-swarm"
Q=data/codex/astra/qbox-opus/qd.py
python3 -B $Q ~/meow-redteam/solo/runs/lc_mTd0/ladder_portals_1-seed1-side0/game.replay 0 4
python3 -B $Q ~/meow-redteam/solo/runs/pc_mNps/ladder_portals_1-seed2-side0/game.replay 0 4
python3 -B $Q ~/meow-redteam/solo/runs/lc_mNps/ladder_portals_1-seed1-side1/game.replay 1 4
