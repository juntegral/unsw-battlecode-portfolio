#!/bin/zsh
cd "~/01. Project/개인 프로젝트/unsw-swarm"
deadline=$(( $(date +%s) + 5400 ))
while [ $(date +%s) -lt $deadline ]; do
  o="$(node tools/online.js battle 1029008 2>&1; node tools/online.js battle 1029023 2>&1)"
  n=$(echo "$o" | grep -c "completed")
  [ "$n" -ge 30 ] && break
  sleep 60
done
node tools/submit.js activate 15011 --confirm > data/online/smoke/stride2-activate.log 2>&1
if node tools/submit.js active 2>&1 | grep -q "15011"; then
  printf '✅ done, swapped back: v61 is active again. both halves finished (30 games each vs test4 + WeHaveQuizzes, same maps). comparison coming on #21\n' > data/guide/a2.txt
else
  printf '⚠️ stride test finished but v61 could NOT be re-activated automatically. please don'"'"'t upload; run: node tools/submit.js activate 15011 --confirm\n' > data/guide/a2.txt
fi
python3 tools/meowbot.py --announce-file data/guide/a2.txt
node tools/online.js download 1027806,1027963 --out smoke/stride-old --purpose "pair stride-test old" > data/online/smoke/stride2-dl.log 2>&1
node tools/online.js download 1029008,1029023 --out smoke/stride-new --purpose "pair stride-test new" >> data/online/smoke/stride2-dl.log 2>&1
touch data/online/smoke/stride2-finished
