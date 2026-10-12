#!/bin/zsh
# Which local games are running: count of bot processes per bot folder, and the load.
date "+%H:%M:%S"; uptime | sed 's/.*load/load/'
ps -Ao command | grep "/bot$" | grep -v grep | sed 's/.*bots\///' | sort | uniq -c | sort -rn | head -n 30
echo "engine processes: $(pgrep -f 'unswbc|engine' | wc -l | tr -d ' ')"
