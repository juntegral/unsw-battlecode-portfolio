#!/bin/bash
# GitHub main을 unsw-arena 내용으로 교체하는 merge (역사는 둘 다 보존, 강제 push 없음).
# 옛 main은 태그 backup/main-before-arena로 남는다. 일반 터미널에서 1번 실행.
set -e
cd "$(dirname "$0")/.."
ROOT="$PWD"
git add CLAUDE.md README.md
git commit -m "docs: plumber submits new versions only, no new online battles" || true
git fetch origin
git push origin main:arena
git tag -f backup/main-before-arena origin/main
rm -rf /tmp/merge-main
git worktree prune
git worktree add --detach /tmp/merge-main origin/main
cd /tmp/merge-main
git merge --allow-unrelated-histories --no-commit --no-ff main || true
git read-tree --reset -u main
git commit -m "Merge arena into main: replace outdated main with unsw-arena"
git push origin HEAD:main
git push origin backup/main-before-arena
cd "$ROOT"
git worktree remove --force /tmp/merge-main
git merge --ff-only origin/main
echo "완료:"
git log --oneline -3
