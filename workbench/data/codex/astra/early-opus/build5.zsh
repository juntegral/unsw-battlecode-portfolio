cd ~/meow-redteam/solo
SW=$(cat "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/seen/one14.switches")
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_cp0=$SW,CENTER_PULL:0.0" 2>&1 | tail -1
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_st4=$SW,TR_STALL_ROUNDS:4" 2>&1 | tail -1
grep -n "^constexpr double CENTER_PULL\|^constexpr int TR_STALL_ROUNDS" bots/ea_cp0/main.cpp bots/ea_st4/main.cpp
