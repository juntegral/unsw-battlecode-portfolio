#!/bin/zsh
# Inventory for the wrap-up: every project folder, whether it is a git repository, its remote, branch, unpushed and
# uncommitted state, and sizes. Read-only.
for d in "~/01. Project/개인 프로젝트/battlecode" "~/01. Project/개인 프로젝트/unsw-swarm" ~/meow-redteam ~/meow-redteam/solo ~/meow-loop; do
  echo "=== $d"
  [ -d "$d" ] || { echo "  (missing)"; continue; }
  du -sh "$d" 2>/dev/null | cut -f1 | sed 's/^/  size /'
  if git -C "$d" rev-parse --show-toplevel > /dev/null 2>&1; then
    echo "  toplevel $(git -C "$d" rev-parse --show-toplevel)"
    echo "  remote $(git -C "$d" remote -v | head -1 | cut -c1-100)"
    echo "  branch $(git -C "$d" branch --show-current)  head $(git -C "$d" log --oneline -1 | cut -c1-80)"
    echo "  branches: $(git -C "$d" branch | tr '\n' ' ' | cut -c1-200)"
    echo "  worktrees: $(git -C "$d" worktree list | wc -l | tr -d ' ')"
    echo "  uncommitted: modified $(git -C "$d" status --porcelain | grep -vc '^??') untracked $(git -C "$d" status --porcelain | grep -c '^??')"
    echo "  unpushed commits on this branch: $(git -C "$d" log --oneline @{u}.. 2>/dev/null | wc -l | tr -d ' ')"
  else
    echo "  NOT a git repository"
  fi
done
echo "=== sizes inside unsw-swarm"
du -sh "~/01. Project/개인 프로젝트/unsw-swarm"/* 2>/dev/null | sort -rh | head -n 12
echo "=== sizes inside meow-redteam"
du -sh ~/meow-redteam/* 2>/dev/null | sort -rh | head -n 10
du -sh ~/meow-redteam/solo/* 2>/dev/null | sort -rh | head -n 8
