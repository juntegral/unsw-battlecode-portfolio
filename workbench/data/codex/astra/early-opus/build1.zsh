cd ~/meow-redteam/solo
SW=$(cat "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/seen/one14.switches")
MKSRC=src/w-early/diag.cpp python3 tools/mkbots.py "ea_diag=$SW" 2>&1 | tail -2
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_off=" 2>&1 | tail -2
shasum bots/ea_off/bot
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_hs=$SW,HARVEST_SPLIT:true" 2>&1 | tail -2
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_room2=$SW,CHILD_MIN_ROOM:2.0" 2>&1 | tail -2
ls bots/ea_diag bots/ea_hs bots/ea_room2
