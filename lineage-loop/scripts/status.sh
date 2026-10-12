#!/bin/bash
# 루프 현황 한눈에 보기: 워크트리별 웨이브·최근 버전, 배포, 로컬 벤치마크, 배관 데몬.
# usage: scripts/status.sh
cd "$(dirname "$0")/.." || exit 1
DATA="${UNSW_ARENA_DATA:-~/01. Project/개인 프로젝트/unsw-arena-data}"
NODE="$(command -v node || echo ~/.aside/runtime/bin/node)"
PLOG="~/01. Project/개인 프로젝트/UNSW/lineages/_daemon/log.md"
echo "== $(date '+%F %T')"
echo; echo "== 워크트리별 계통"
git worktree list --porcelain 2>/dev/null | awk '/^worktree /{sub(/^worktree /,""); print}' | while read -r wt; do
  br=$(git -C "$wt" branch --show-current 2>/dev/null)
  for d in "$wt"/lineages/*/waves; do
    [ -f "$d/index.log" ] || continue
    L=$(basename "$(dirname "$d")")
    starts=$(grep -c ' start' "$d/index.log"); fb=$(grep -c 'fallback ' "$d/index.log")
    last=$(tail -1 "$d/index.log")
    ready=$(grep -Eo 'ready:[[:space:]]*r[0-9]+' "$wt/lineages/$L/NOTES.md" 2>/dev/null | tail -1)
    stop=""; [ -f "$wt/lineages/$L/STOP" ] && stop=" [STOP]"
    echo "- $L ($br): 웨이브 ${starts}회, 대체모델 ${fb}회, 최근 ${ready:-ready 없음}${stop}"
    echo "    마지막: $last"
    if [ -f "$d/last.json" ]; then
      "$NODE" -e 'const s=require(process.argv[1]); console.log("    완료 상태: "+s.wave+" / "+s.outcome+" / "+s.reason)' "$d/last.json"
    fi
  done
done
echo; echo "== 배포 스냅숏 (웨이브 루프가 내보낸 버전)"
ls "$DATA/releases" 2>/dev/null | grep -v sha256 | tr '\n' ' '; echo
echo; echo "== 로컬 벤치마크 (lineages/_eval/PROGRESS.md)"
sed -n '7,40p' "$DATA/eval/PROGRESS.md" 2>/dev/null || echo "(아직 없음)"
echo; echo "== 배관 데몬 최근 기록"
tail -6 "$PLOG" 2>/dev/null
