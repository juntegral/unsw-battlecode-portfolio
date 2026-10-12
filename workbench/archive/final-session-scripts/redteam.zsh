#!/bin/zsh
# Wrap-up: turn ~/meow-redteam (local game rig + the solo bot's source lineage) into a private GitHub repo.
# Replays, compiled bots and logs stay out; the result line and json of every local game go in as one small archive.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam || exit 1
[ -d .git ] || git init -q -b archive
# every local game's result (result.txt + small json), without replays or logs
find solo/runs -type f \( -name 'result.txt' -o -name '*.json' -o -name 'run.log' \) -size -200k > $T/runs-results.list
tar -cJf solo/runs-results.tar.xz -T $T/runs-results.list
echo "runs-results: $(wc -l < $T/runs-results.list | tr -d ' ') files -> $(du -h solo/runs-results.tar.xz | cut -f1)"
git add .gitignore solo/runs-results.tar.xz
git add --pathspec-from-file=$T/add-redteam.txt 2>&1 | tail -n 3
python3 -B $T/scan.py ~/meow-redteam --staged | tail -n 6
git status --short | grep -v '^A ' | head -n 12
echo "staged: $(git diff --cached --name-only | wc -l | tr -d ' ')"
