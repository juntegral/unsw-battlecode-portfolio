cd ~/meow-redteam/solo
SW=$(cat "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/seen/one14.switches")
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_ex10=$SW,EXPLORE_GAIN:10.0" 2>&1 | tail -1
grep -n "^constexpr double EXPLORE_GAIN" bots/ea_ex10/main.cpp
