#!/bin/zsh
# Arms with the existing queen home leash (never tested): one16 + QUEEN_HOME_LEASH 3 and 6; head to head against mD16.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
SW=$(cat $T/one16.switches)
MKSRC=src/w-shed/main.cpp python3 tools/mkbots.py "mHl3=$SW,QUEEN_HOME_LEASH:3" 2>&1 | tail -n 1
MKSRC=src/w-shed/main.cpp python3 tools/mkbots.py "mHl6=$SW,QUEEN_HOME_LEASH:6" 2>&1 | tail -n 1
shasum bots/mHl3/bot bots/mHl6/bot | cut -c1-12,41-
for a in mHl3 mHl6; do nohup zsh $T/h2h17.zsh $a > $T/h2h17-$a.out 2>&1 & done
sleep 1; pgrep -fl "tmp/h2h17" | cut -c1-90
date "+%H:%M:%S"; uptime | sed 's/.*load/load/'
python3 solo/tools/h2h_tally.py | grep "_v16" | cut -c1-44
