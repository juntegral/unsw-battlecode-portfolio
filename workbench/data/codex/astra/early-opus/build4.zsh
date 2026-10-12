cd ~/meow-redteam/solo
SW=$(cat "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/seen/one14.switches")
A=${SW/HEADING_TIE_ROUNDS:12/HEADING_TIE_ROUNDS:0}
B=${A/HEADING_TIE:1.5/HEADING_TIE:12.0}
C=${A/HEADING_TIE:1.5/HEADING_TIE:25.0}
D=${SW/HEADING_TIE:1.5/HEADING_TIE:12.0}
D=${D/HEADING_TIE_ROUNDS:12/HEADING_TIE_ROUNDS:60}
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_ht12=$B" 2>&1 | tail -1
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_ht25=$C" 2>&1 | tail -1
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_ht12r60=$D" 2>&1 | tail -1
grep -n "^constexpr double HEADING_TIE\|^constexpr int HEADING_TIE_ROUNDS" bots/ea_ht12/main.cpp bots/ea_ht25/main.cpp bots/ea_ht12r60/main.cpp
