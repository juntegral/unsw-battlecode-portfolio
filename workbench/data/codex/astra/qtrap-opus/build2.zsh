cd ~/meow-redteam/solo
ONE=$(cat ~/.claude/jobs/e2109d93/tmp/one17.switches)
MKSRC=src/w-qtrap/main.cpp python3 tools/mkbots.py "qtoff2=" "qtid2=$ONE" "qtt=$ONE,QUEEN_CORRIDOR_MATE:true,QUEEN_CORRIDOR_TREE:true"
shasum bots/qtoff2/bot bots/qtid2/bot bots/qtt/bot bots/mD17/bot
