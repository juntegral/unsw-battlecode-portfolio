cd ~/meow-redteam/solo
O=$(cat ~/.claude/jobs/e2109d93/tmp/one15.switches)
export MKSRC=src/w-qbox/main.cpp
python3 tools/mkbots.py "qbA3=" "qbO15d=$O" "qbK2=$O,QUEEN_ROOM_KEEP:2" "qbK5=$O,QUEEN_ROOM_KEEP:5"
shasum bots/qbA3/bot bots/qbO15d/bot bots/mD15/bot bots/qbK2/bot bots/qbK5/bot
