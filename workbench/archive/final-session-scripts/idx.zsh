#!/bin/zsh
# Is the qexit source with the one15 values (new switch off) the same PLAYER as the live bot, although the binary differs?
# Same four maps, both seats, against m3base; compare replays byte for byte (bot names have equal length).
cd ~/meow-redteam/solo || exit 1
T=~/.claude/jobs/e2109d93/tmp
MKSRC=src/w-qexit/main.cpp python3 tools/mkbots.py "mXl5=$(cat $T/one15.switches)" 2>&1 | tail -n 1
cd ~/meow-redteam || exit 1
rm -rf solo/runs/idx_mXl5 solo/runs/idx_mD15
for n in ladder_queen_of_spades_1 ladder_australia_1 gx_islands_24x12_911201 gx_rooms_24x12_911001; do
  m=$(ls maps/*/$n.map | head -1)
  for a in mXl5 mD15; do
    ./play.sh solo/bots/$a solo/bots/m3base $m 1 solo/runs/idx_$a/$n-seed1-side0 > /dev/null 2>&1 &
    ./play.sh solo/bots/m3base solo/bots/$a $m 1 solo/runs/idx_$a/$n-seed1-side1 > /dev/null 2>&1 &
  done
done
wait
for d in solo/runs/idx_mXl5/*/; do
  n=$(basename $d); a=$d/game.replay; b=solo/runs/idx_mD15/$n/game.replay
  echo "$n size $(wc -c < $a | tr -d ' ')/$(wc -c < $b | tr -d ' ') differing bytes $(cmp -l $a $b 2>/dev/null | wc -l | tr -d ' ')"
done
echo "idx-done $(date '+%T')" >> solo/runs/run.log
