#!/bin/zsh
# Wrap-up, read-only: what the worktrees with uncommitted work hold (changed and untracked files with sizes).
for W in ~/meow-bigmap ~/meow-dev ~/meow-dev2 ~/meow-dev3 ~/meow-loop ~/meow-queen; do
  echo "=== $W  branch $(git -C $W branch --show-current)  head $(git -C $W log --oneline -1 | cut -c1-70)"
  git -C $W status --short | while read -r st f; do
    if [ -d "$W/$f" ]; then echo "  $st $f  (dir $(du -sh "$W/$f" | cut -f1), $(find "$W/$f" -type f | wc -l | tr -d ' ') files)"; else echo "  $st $f  ($(wc -c < "$W/$f" 2>/dev/null | tr -d ' ') bytes)"; fi
  done | cut -c1-150
  git -C $W diff --stat | tail -n 1
done
B="~/01. Project/개인 프로젝트/battlecode"
echo "=== card/17 local vs origin"; git -C "$B" log --oneline origin/card/17..card/17 | cut -c1-100
echo "=== main checkout .claude"; du -sh "$B/.claude" | cut -f1; ls "$B/.claude" | head
