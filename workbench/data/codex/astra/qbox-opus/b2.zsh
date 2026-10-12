cd ~/meow-redteam/solo
O=$(cat ~/.claude/jobs/e2109d93/tmp/one15.switches)
export MKSRC=src/w-qbox/main.cpp
python3 tools/mkbots.py "qbA1=" "qbO15b=$O" "qbRK=$O,QUEEN_ROOM_KEEP:12"
shasum bots/qbA1/bot bots/qbO15b/bot bots/mD15/bot bots/qbRK/bot
