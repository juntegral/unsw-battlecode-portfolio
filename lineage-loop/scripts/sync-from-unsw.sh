#!/bin/bash
# Aside(UNSW 프로젝트)에서 돌던 계통 g1/g2의 최신 상태를 이 저장소로 가져온다. Orca에서 처음 시작하기 직전에 1번 실행.
# 그 뒤에는 Aside의 g1/g2 감시 루틴을 반드시 멈춘다(같은 계통을 두 곳에서 동시에 고치지 않도록).
set -e
cd "$(dirname "$0")/.."
U="~/01. Project/개인 프로젝트/UNSW"
for L in ${@:-g1 g2}; do
  rsync -a --exclude replays --exclude logs --exclude waves --exclude '*.replay' --exclude .unswbc-build --exclude build "$U/lineages/$L/" "lineages/$L/"
  echo "synced $L"
done
git add -A lineages && git commit -qm "sync lineages from UNSW/Aside" && echo "committed" || echo "nothing to commit"
