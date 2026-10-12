cd "~/01. Project/개인 프로젝트/unsw-swarm"
look() {
  p=$(ls data/online/live-one1/b*/M$1.replay data/online/smoke/*/M$1.replay 2>/dev/null | head -1)
  echo "=== $1 dragon $2 r$3-$4 $p"
  python3 data/analysis/ladder/dossier/work/o1_look.py "$p" $1 $2 $3 $4 2>&1 | grep -v eats
}
look 1513846 0 213 215
look 1513846 8 213 215
look 1496711 0 47 49
look 1496711 36 47 49
look 1518919 1 38 40
look 1518919 14 38 40
