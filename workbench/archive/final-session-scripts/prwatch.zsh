#!/bin/zsh
# Wake when the team repo's pull requests change.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
python3 tools/team_watch.py --prs --wait 86400
