#!/bin/zsh
# Build label reports for the one12 and one13 sets so their per-game rows are in the cache, then print pearls by r100 per map.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
R=data/analysis/ladder/dossier/online/label_report.py
nice -n 5 python3 -B $R one13-c1:old --ref one12-c1:old --ref one13-c2:old 2>&1 | tail -n 1 | cut -c1-60
nice -n 5 python3 -B $R one13-p1:old --ref one12-p1:old --ref one11-p1:old 2>&1 | tail -n 1 | cut -c1-60
nice -n 5 python3 -B $R one13-k1:old --ref one12-k1:old --ref one11-k1:old 2>&1 | tail -n 1 | cut -c1-60
python3 ~/.claude/jobs/e2109d93/tmp/portalcheck.py
