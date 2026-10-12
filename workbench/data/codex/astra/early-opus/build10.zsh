cd ~/meow-redteam/solo
SW=$(cat "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/seen/one14.switches")
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_off3=" 2>&1 | tail -1
shasum bots/ea_off3/bot
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_one14c=$SW" 2>&1 | tail -1
shasum bots/ea_one14c/bot bots/mNps/bot
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_ex10nq40=$SW,EXPLORE_GAIN:10.0,EXPLORE_NO_QUEEN:true,EXPLORE_ROUNDS:40" 2>&1 | tail -1
