#!/bin/zsh
# QUEEN_BLIND_STALL (lead, 1 constant + 1 condition): while the side still has 2 or fewer dragons at that round or later,
# the queen may scout a blind portal again. Hash checks, then mC19 = combo A + QUEEN_BLIND_STALL 20 on the blind start box
# (both seats), Portals (both seats) and Stripes against m3base, beside mA19 and mD18.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
MKSRC=src/w-one19/main.cpp python3 tools/mkbots.py "mF19=" 2>&1 | tail -n 1
MKSRC=src/w-one19/main.cpp python3 tools/mkbots.py "mL19=$(cat $T/one18.switches)" 2>&1 | tail -n 1
MKSRC=src/w-one19/main.cpp python3 tools/mkbots.py "mA19b=$(cat $T/one19A.switches)" 2>&1 | tail -n 1
echo "$(cat $T/one19A.switches),QUEEN_BLIND_STALL:20" > $T/one19C.switches
MKSRC=src/w-one19/main.cpp python3 tools/mkbots.py "mC19=$(cat $T/one19C.switches)" 2>&1 | tail -n 1
shasum bots/mF19/bot bots/mL19/bot bots/mD18/bot bots/mA19b/bot bots/mA19/bot bots/mC19/bot | cut -c1-12,41-
cd ~/meow-redteam || exit 1
for m in maps/un2/ua_boxnp_320.map maps/ladder/ladder_portals_1.map maps/ladder/ladder_stripes_1.map; do
  N=$(basename $m .map)
  for a in mC19 mA19 mD18; do
    for s in 0 1; do
      O=solo/runs/st_$a/$N-seed1-side$s
      [ -e $O/result.txt ] && continue
      if [ $s = 0 ]; then ./play.sh solo/bots/$a solo/bots/m3base $m 1 $O > /dev/null 2>&1 &
      else ./play.sh solo/bots/m3base solo/bots/$a $m 1 $O > /dev/null 2>&1 &; fi
    done
  done
  wait
done
echo "stall19-done $(date '+%T')" >> solo/runs/run.log
