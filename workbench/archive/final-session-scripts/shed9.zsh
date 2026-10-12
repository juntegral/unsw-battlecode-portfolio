#!/bin/zsh
# mSh9 = one16 + QS_SHED_MAX 9 (the queen's "keep 2" emergency split only at length 9 or shorter). Pairs against the live
# bot's own games: each of mSh9 and mD16 against m3base on the 16 ladder maps (seat 0; Slithery, Trauma, Islands, Around UNSW
# and Australia also seat 1), 16 games at a time. Then a table of result, pearls and dragons at r100.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
MKSRC=src/w-shed/main.cpp python3 tools/mkbots.py "mSh9=$(cat $T/one16.switches),QS_SHED_MAX:9" 2>&1 | tail -n 1
shasum bots/mSh9/bot | cut -c1-12
cd ~/meow-redteam || exit 1
n=0
for m in maps/ladder/ladder_*.map; do
  N=$(basename $m .map)
  for a in mSh9 mD16; do
    [ -e solo/runs/sh_$a/$N-seed1-side0/result.txt ] || { ./play.sh solo/bots/$a solo/bots/m3base $m 1 solo/runs/sh_$a/$N-seed1-side0 > /dev/null 2>&1 &; n=$((n+1)); }
    case $N in *slithery*|*trauma*|*islands*|*around*|*australia*)
      [ -e solo/runs/sh_$a/$N-seed1-side1/result.txt ] || { ./play.sh solo/bots/m3base solo/bots/$a $m 1 solo/runs/sh_$a/$N-seed1-side1 > /dev/null 2>&1 &; n=$((n+1)); } ;;
    esac
    [ $((n % 16)) -eq 0 ] && [ $n -gt 0 ] && wait
  done
done
wait
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
python3 -B $T/lcheck.py sh_mD16 sh_mSh9 > $T/lcheck-mSh9.txt 2>&1
echo "sh9-done $(date '+%T')" >> ~/meow-redteam/solo/runs/run.log
