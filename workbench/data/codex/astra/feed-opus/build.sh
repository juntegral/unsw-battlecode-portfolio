#!/bin/zsh
cd ~/meow-redteam/solo
SW=$(cat ~/.claude/jobs/e2109d93/tmp/one17.switches)
python3 tools/mkbots.py "fdL=$SW" &
python3 tools/mkbots.py "fd400=$SW,QUEEN_GAME_FEED_ROUND:400,QUEEN_SAFE_ROUND:400" &
python3 tools/mkbots.py "fdNo=$SW,QUEEN_GAME_FEED_ROUND:0,QUEEN_SAFE_ROUND:0,ENDGAME_ROUND:501,FEED_CAP_UNITS:0" &
python3 tools/mkbots.py "fd200=$SW,QUEEN_GAME_FEED_ROUND:200,QUEEN_SAFE_ROUND:200" &
python3 tools/mkbots.py "fdR4=$SW,FEED_LEN_RATIO:4" &
wait
shasum bots/fdL/bot bots/mD17/bot bots/fd400/bot bots/fdNo/bot bots/fd200/bot bots/fdR4/bot
