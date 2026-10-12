cd ~/meow-redteam/solo
ONE=$(cat ~/.claude/jobs/e2109d93/tmp/one17.switches)
MKSRC=src/w-qtrap/main.cpp python3 tools/mkbots.py "qtm2=$ONE,QUEEN_CORRIDOR_MATE:true"
shasum bots/qtm2/bot bots/qtm/bot
