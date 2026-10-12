#!/bin/zsh
# sight-opus: arms = one17 values with the sight constants changed. No source change.
cd $HOME/meow-redteam/solo
SW=$(cat ~/.claude/jobs/e2109d93/tmp/one17.switches)
export MKSRC=src/solo/main.cpp
python3 tools/mkbots.py "sg_L=$SW" > /dev/null 2>&1 &
python3 tools/mkbots.py "sg_f4=${SW/QUEEN_FAR_HEADS:2/QUEEN_FAR_HEADS:4}" > /dev/null 2>&1 &
python3 tools/mkbots.py "sg_f6=${SW/QUEEN_FAR_HEADS:2/QUEEN_FAR_HEADS:6}" > /dev/null 2>&1 &
python3 tools/mkbots.py "sg_f8=${SW/QUEEN_FAR_HEADS:2/QUEEN_FAR_HEADS:8}" > /dev/null 2>&1 &
python3 tools/mkbots.py "sg_e3=$SW,QUEEN_EDGE_REACH:3" > /dev/null 2>&1 &
python3 tools/mkbots.py "sg_f8e3=${SW/QUEEN_FAR_HEADS:2/QUEEN_FAR_HEADS:8},QUEEN_EDGE_REACH:3" > /dev/null 2>&1 &
wait
shasum bots/mD17/bot bots/sg_L/bot bots/sg_f4/bot bots/sg_f6/bot bots/sg_f8/bot bots/sg_e3/bot bots/sg_f8e3/bot
date +%H:%M:%S
