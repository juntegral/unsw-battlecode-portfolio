#!/bin/zsh
D="~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/maps-sonnet"
cd "$D"
python3 -I convert.py 1517698 out/cmp_portals.map
python3 -I convert.py 1517689 out/cmp_stripes.map
python3 -I cmp.py ~/meow-redteam/maps/ladder/ladder_portals_1.map out/cmp_portals.map
python3 -I cmp.py ~/meow-redteam/maps/ladder/ladder_stripes_1.map out/cmp_stripes.map
tail -2 ~/meow-redteam/maps/ladder/ladder_portals_1.map | cat -A | cut -c1-40
tail -2 out/cmp_portals.map | cat -A | cut -c1-40
for p in "1517693 queen_of_spades" "1517697 trauma" "1517695 trophy" "1517692 default" "1517696 devil" "1517688 maze" "1517685 weakhold"; do
  set -- ${=p}
  python3 -I convert.py $1 "$HOME/meow-redteam/maps/ladder/ladder_$2_1.map"
done
