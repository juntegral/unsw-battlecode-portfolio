#!/bin/zsh
# Wrap-up: pack the bulk data of unsw-swarm/data (replays, per-game json, derived tables) into xz archives split below
# GitHub's 2 GB asset limit and attach them to a release of the private repo. One folder at a time, parts removed
# after a verified upload, so at most a few GB of scratch space is used. Nothing in data/ is changed or deleted.
S="~/01. Project/개인 프로젝트/unsw-swarm"
T=~/.claude/jobs/e2109d93/tmp
O=$T/rel; mkdir -p $O
TAG=data-2026-10-10
REPO=juntegral/unsw-swarm
cd "$S" || exit 1
gh release view $TAG --repo $REPO > /dev/null 2>&1 || gh release create $TAG --repo $REPO --target wrapup-2026-10-10 \
  --title "Contest data 2026-10-10 (replays and derived tables)" \
  --notes "Bulk data that is not in git: online replays (our games, ladder, top teams), local study replays, derived tables. Each archive is a tar.xz split into parts. Restore one with: cat NAME.tar.xz.part-* | xz -d | tar -xf - (run inside the repo's data/ folder, or data/online/ for the online-* archives). See docs/retro/00-README.md." || exit 1
pack() {  # name, base dir, folder
  local name=$1 base=$2 dir=$3
  if grep -q "^DONE $name\$" $O/done.txt 2>/dev/null; then echo "skip $name"; return; fi
  echo "$(date +%H:%M:%S) pack $name ($(du -sh "$base/$dir" | cut -f1))"
  rm -f $O/$name.tar.xz.part-*
  tar -cf - --exclude .DS_Store --exclude __pycache__ -C "$base" "$dir" | xz -T0 -6 | split -b 1900m - $O/$name.tar.xz.part-
  (cd $O && shasum -a 256 $name.tar.xz.part-* >> SHA256SUMS.txt)
  echo "$(date +%H:%M:%S) upload $name: $(ls $O/$name.tar.xz.part-* | wc -l | tr -d ' ') parts, $(du -ch $O/$name.tar.xz.part-* | tail -1 | cut -f1)"
  for p in $O/$name.tar.xz.part-*; do
    ok=0
    for try in 1 2 3; do
      if gh release upload $TAG "$p" --repo $REPO --clobber; then ok=1; break; fi
      echo "retry $try $p"; sleep 20
    done
    [ $ok = 1 ] || { echo "UPLOAD FAILED $p"; return 1; }
  done
  echo "DONE $name" >> $O/done.txt
  rm -f $O/$name.tar.xz.part-*
  echo "$(date +%H:%M:%S) done $name"
}
pack online-dl-20261003 data/online dl-20261003 || exit 1
pack online-live-one1 data/online live-one1 || exit 1
pack online-smoke data/online smoke || exit 1
pack online-ladder data/online ladder || exit 1
pack online-top1 data/online top1 || exit 1
pack online-top3 data/online top3 || exit 1
pack online-dl-20261004 data/online dl-20261004 || exit 1
pack local data local || exit 1
pack analysis data analysis || exit 1
pack codex data codex || exit 1
gh release upload $TAG $O/SHA256SUMS.txt --repo $REPO --clobber
echo "$(date +%H:%M:%S) ALL DONE"
gh release view $TAG --repo $REPO --json assets -q '.assets[] | "\(.name) \(.size)"'
