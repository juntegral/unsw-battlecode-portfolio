cd ~/meow-redteam
for bot in ub_cmax mD17; do
  mkdir -p solo/runs/ub_a_$bot
  for name in ladder_maze_1 ladder_trauma_1 ladder_slithery_fight_1; do
    out=solo/runs/ub_a_$bot/$name-seed7-side0
    if [ -e $out/result.txt ]; then continue; fi
    ./play.sh solo/bots/$bot solo/bots/m3base maps/ladder/$name.map 7 $out > $out.log 2>&1 &
  done
  wait
done
cd "~/01. Project/개인 프로젝트/unsw-swarm"
for bot in ub_cmax mD17; do
  echo "== $bot"
  python3 -B data/codex/astra/unB-opus/health.py ub_a_$bot ladder_ | cut -c1-230
done
date
