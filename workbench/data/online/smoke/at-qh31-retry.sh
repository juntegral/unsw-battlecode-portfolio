#!/bin/zsh
# retry of the #31 pair once the hourly allowance (60 games) is back
cd "~/01. Project/개인 프로젝트/unsw-swarm"
until [ "$(date +%Y%m%d%H%M%S)" -ge 20261005015030 ]; do sleep 5; done
exec data/online/smoke/at-qh31.sh
