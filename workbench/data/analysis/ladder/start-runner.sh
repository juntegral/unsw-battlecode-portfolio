#!/bin/zsh
# First cycle now (analyst at xhigh), then the hourly loop until the freeze. Started detached.
cd "~/01. Project/개인 프로젝트/unsw-swarm" || exit 1
python3 tools/ladder_hourly.py --once --first
exec python3 tools/ladder_hourly.py
