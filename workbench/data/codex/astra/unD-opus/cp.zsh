mkdir -p ~/meow-redteam/maps/un2
for f in "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/unseen/maps/"un_*.map; do
  cp "$f" ~/meow-redteam/maps/un2/ud_$(basename "$f")
done
ls ~/meow-redteam/maps/un2 | wc -l
