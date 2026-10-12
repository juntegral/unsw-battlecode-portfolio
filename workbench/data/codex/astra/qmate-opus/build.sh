cd ~/meow-redteam/solo
SW=$(cat ~/.claude/jobs/e2109d93/tmp/one17.switches)
MKSRC=src/w-qmate/main.cpp python3 tools/mkbots.py "qm_off=" "qm_17=$SW" "qm_on=$SW,QUEEN_ROOM_MATES:true" 2>&1 | tail -15
shasum bots/qm_off/bot bots/qm_17/bot bots/qm_on/bot bots/mD17/bot
date
