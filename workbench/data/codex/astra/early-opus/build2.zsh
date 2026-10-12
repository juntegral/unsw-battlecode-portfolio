cd ~/meow-redteam/solo
SW=$(cat "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/seen/one14.switches")
A=${SW/HEADING_TIE_ROUNDS:12/HEADING_TIE_ROUNDS:0}
B=${A/HEADING_TIE:1.5/HEADING_TIE:4.0}
C=${SW/HEADING_TIE_ROUNDS:12/HEADING_TIE_ROUNDS:60}
echo $A | tr ',' '\n' | grep HEADING
echo $B | tr ',' '\n' | grep HEADING
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_ht0=$A" 2>&1 | tail -1
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_ht4=$B" 2>&1 | tail -1
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_ht60=$C" 2>&1 | tail -1
MKSRC=src/w-early/main.cpp python3 tools/mkbots.py "ea_one14=$SW" 2>&1 | tail -1
shasum bots/ea_one14/bot bots/mNps/bot
