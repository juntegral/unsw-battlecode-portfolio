cd ~/meow-redteam/solo
SW=$(cat "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/seen/one14.switches")
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_ce=$SW,CRAMPED_EAT:true" 2>&1 | tail -1
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_cent6=$SW,CRAMPED_EAT:true,NO_TAIL_ROOM:6" 2>&1 | tail -1
grep -n "^constexpr bool CRAMPED_EAT\|^constexpr int NO_TAIL_ROOM" bots/ea_ce/main.cpp bots/ea_cent6/main.cpp
