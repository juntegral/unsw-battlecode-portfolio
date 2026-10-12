cd ~/meow-redteam/solo
SW=$(cat "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/seen/one14.switches")
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_nt6=$SW,NO_TAIL_ROOM:6" 2>&1 | tail -1
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_nt6st4=$SW,NO_TAIL_ROOM:6,TR_STALL_ROUNDS:4" 2>&1 | tail -1
grep -n "^constexpr int NO_TAIL_ROOM\|^constexpr int TR_STALL_ROUNDS" bots/ea_nt6/main.cpp bots/ea_nt6st4/main.cpp
