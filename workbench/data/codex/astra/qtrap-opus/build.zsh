cd ~/meow-redteam/solo
ONE=$(cat ~/.claude/jobs/e2109d93/tmp/one17.switches)
MKSRC=src/w-qtrap/main.cpp python3 tools/mkbots.py "qtoff=" "qtid=$ONE" "qtm=$ONE,QUEEN_CORRIDOR_MATE:true"
shasum bots/qtoff/bot bots/qtid/bot bots/qtm/bot bots/mD17/bot
