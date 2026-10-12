cd ~/meow-redteam/solo
SW=$(cat "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/seen/one14.switches")
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_tw05=$SW,WEIGHT_TERRITORY:0.5" 2>&1 | tail -1
grep -n "^constexpr double WEIGHT_TERRITORY\|^constexpr double TERRITORY_DECAY" bots/ea_tw05/main.cpp
