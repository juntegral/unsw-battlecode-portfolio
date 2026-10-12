#!/bin/zsh
# Wrap-up inventory 3, read-only.
S="~/01. Project/개인 프로젝트/unsw-swarm"
B="~/01. Project/개인 프로젝트/battlecode"
T=~/.claude/jobs/e2109d93/tmp
echo "=== tools"; which zstd xz pigz gh 2>&1 | head; df -h ~ | tail -1
echo "=== job tmp"; du -sh $T | cut -f1; ls $T | wc -l; du -sh $T/* 2>/dev/null | sort -rh | head -8
echo "=== local branches vs origin (same name)"
git -C "$B" ls-remote --heads origin > $T/remote-heads.txt 2>/dev/null
for b in $(git -C "$B" for-each-ref refs/heads --format='%(refname:short)'); do
  L=$(git -C "$B" rev-parse "$b"); R=$(grep "refs/heads/$b\$" $T/remote-heads.txt | cut -f1)
  if [ -z "$R" ]; then
    N=$(git -C "$B" rev-list --count "$b" --not --remotes=origin)
    echo "LOCAL-ONLY $b  commits not on any origin branch: $N  ($(git -C "$B" log -1 --format='%ad %s' --date=short "$b" | cut -c1-70))"
  elif [ "$L" != "$R" ]; then
    echo "DIFFERS    $b  ahead $(git -C "$B" rev-list --count origin/$b..$b 2>/dev/null) behind $(git -C "$B" rev-list --count $b..origin/$b 2>/dev/null)"
  fi
done
echo "remote branches: $(wc -l < $T/remote-heads.txt | tr -d ' ')"
echo "=== worktrees with changes"
git -C "$B" worktree list --porcelain | grep '^worktree ' | cut -c10- | while read -r W; do
  M=$(git -C "$W" status --porcelain 2>/dev/null | grep -vc '^??'); U=$(git -C "$W" status --porcelain 2>/dev/null | grep -c '^??')
  [ "$M" != "0" ] || [ "$U" != "0" ] && echo "$M modified $U untracked  $(git -C "$W" branch --show-current)  $W"
done | cut -c1-200
echo "=== stashes: $(git -C "$B" stash list | wc -l | tr -d ' ')"
echo "=== meow-redteam files over 5MB outside runs and replays"
find ~/meow-redteam -type f -size +5M -not -name '*.replay' -not -path '*/solo/runs/*' -not -path '*/runs/*' 2>/dev/null | head -40 | while read -r f; do echo "$(du -h "$f" | cut -f1) $f"; done | cut -c1-170
echo "=== engine"; du -sh ~/meow-redteam/engine ~/meow-redteam/starter ~/meow-redteam/docs ~/meow-redteam/tools ~/meow-redteam/mytools ~/meow-redteam/notes 2>/dev/null
echo "=== unsw-swarm docs head"; head -n 12 "$S/docs/HANDOVER-2026-10-09.md" | cut -c1-200
echo "=== memory dir"; ls ~/.claude/projects/-Users-jun-01--Project---------battlecode/memory | wc -l
echo "=== loop runner state"; ls "$B/work/loop" 2>/dev/null | head -20
