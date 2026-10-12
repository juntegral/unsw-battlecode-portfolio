#!/bin/zsh
# Wrap-up inventory, read-only: what is not on GitHub yet in each place, what is ignored, how big, what still runs.
S="~/01. Project/개인 프로젝트/unsw-swarm"
B="~/01. Project/개인 프로젝트/battlecode"
echo "=== gh account"; gh api user -q .login 2>&1 | head -1
gh repo list --limit 30 --json name,visibility,diskUsage -q '.[] | "\(.name) \(.visibility) \(.diskUsage)KB"' 2>&1 | head -30
echo "=== unsw-swarm status"; git -C "$S" status --short | cut -c1-120
echo "--- unpushed"; git -C "$S" log --oneline @{u}.. | cut -c1-100
echo "--- .gitignore"; cat "$S/.gitignore" 2>/dev/null | head -60
echo "--- info/exclude"; grep -v '^#' "$S/.git/info/exclude" 2>/dev/null | head -20
echo "--- tracked files: $(git -C "$S" ls-files | wc -l | tr -d ' ')  .git size: $(du -sh "$S/.git" | cut -f1)"
echo "--- data sizes"; du -sh "$S"/data/* 2>/dev/null | sort -rh | head -25
echo "--- docs"; ls "$S/docs" | head -60
echo "=== battlecode branches (local, upstream, ahead/behind)"
git -C "$B" for-each-ref refs/heads --format='%(refname:short)|%(upstream:short)|%(upstream:track)' | cut -c1-110
echo "--- untracked in main checkout"; git -C "$B" status --short | cut -c1-120
echo "--- info/exclude"; grep -v '^#' "$B/.git/info/exclude" 2>/dev/null | head -20
echo "--- open PRs"; (cd "$B" && gh pr list --state open --json number,title,headRefName -q '.[] | "#\(.number) \(.headRefName) \(.title)"' | cut -c1-140)
echo "=== meow-loop"; git -C ~/meow-loop rev-parse --git-common-dir; git -C ~/meow-loop status --short | cut -c1-120 | head -20
echo "=== meow-redteam top"; ls ~/meow-redteam | head -40
echo "--- solo"; ls ~/meow-redteam/solo | head; echo "src dirs: $(ls ~/meow-redteam/solo/src | wc -l | tr -d ' ')  bots: $(ls ~/meow-redteam/solo/bots | wc -l | tr -d ' ')  runs: $(ls ~/meow-redteam/solo/runs | wc -l | tr -d ' ')"
echo "=== processes"; pgrep -fl "team_watch|meowbot|discord_sync|weak_watch|at-q|runner|cx.sh|codex|collector|mention" | cut -c1-140 | head -30
