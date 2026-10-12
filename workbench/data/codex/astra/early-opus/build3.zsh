cd ~/meow-redteam/solo
SW=$(cat "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/seen/one14.switches")
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_off2=" 2>&1 | tail -1
shasum bots/ea_off2/bot
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_pt4=$SW,PEARL_TAIL_GAIN:4.0" 2>&1 | tail -1
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_pt6=$SW,PEARL_TAIL_GAIN:6.0,PEARL_TAIL_RANGE:24" 2>&1 | tail -1
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_pfd13=$SW,PEARL_FAR_DECAY:13.0" 2>&1 | tail -1
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_one14b=$SW" 2>&1 | tail -1
shasum bots/ea_one14b/bot bots/mNps/bot
