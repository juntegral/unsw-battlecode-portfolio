cd ~/meow-redteam/solo
O=$(cat ~/.claude/jobs/e2109d93/tmp/one15.switches)
export MKSRC=src/w-qbox/main.cpp
python3 tools/mkbots.py "qbA0=" "qbO15=$O" "qbPA=$O,QUEEN_PORTAL_ALL:true"
shasum bots/qbA0/bot bots/qbO15/bot bots/mD15/bot bots/qbPA/bot
