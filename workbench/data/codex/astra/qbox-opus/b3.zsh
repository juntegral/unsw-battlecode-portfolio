cd ~/meow-redteam/solo
O=$(cat ~/.claude/jobs/e2109d93/tmp/one15.switches)
export MKSRC=src/w-qbox/main.cpp
python3 tools/mkbots.py "qbA2=" "qbO15c=$O" "qbRK2=$O,QUEEN_ROOM_KEEP:12"
shasum bots/qbA2/bot bots/qbO15c/bot bots/mD15/bot bots/qbRK2/bot
