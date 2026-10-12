#!/bin/zsh
# Fetch the map Zhe attached in #meow (portal_boomerang.map) with curl, show its head, and play the last-bot candidate on it.
T=~/.claude/jobs/e2109d93/tmp
U=$(python3 -c "
import re
md=open('~/01. Project/개인 프로젝트/unsw-swarm/data/discord/900000000000000004.md').read()
m=re.findall(r'\((https://cdn\.discordapp\.com/attachments/[^)\s]*portal_boomerang\.map[^)\s]*)\)', md)
print(m[-1] if m else '')")
[ -n "$U" ] || { echo "no link"; exit 1; }
M=~/meow-redteam/maps/community/portal_boomerang.map
curl -sL --max-time 30 -o $M "$U"; echo "curl rc $? bytes $(wc -c < $M | tr -d ' ')"
head -n 6 $M | cut -c1-120
cd ~/meow-redteam || exit 1
for a in mC19 mD18; do
  ./play.sh solo/bots/$a solo/bots/m3base $M 1 solo/runs/zh_$a/boomerang-seed1-side0 > /dev/null 2>&1 &
  ./play.sh solo/bots/m3base solo/bots/$a $M 1 solo/runs/zh_$a/boomerang-seed1-side1 > /dev/null 2>&1 &
done
./play.sh solo/bots/mC19 solo/bots/mC19 $M 1 solo/runs/zh_mirror/boomerang-seed1-side0 > /dev/null 2>&1 &
wait
for d in solo/runs/zh_mC19/* solo/runs/zh_mD18/* solo/runs/zh_mirror/*; do echo "$d: $(cat $d/result.txt 2>/dev/null | tr '\n' ' ' | cut -c1-110) | log errors: $(grep -ci 'error\|timeout\|exception\|traceback' $d/engine.log 2>/dev/null)"; done
echo "zhemap-done $(date '+%T')" >> solo/runs/run.log
