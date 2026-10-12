cd ~/meow-redteam/solo
SW=$(cat ~/.claude/jobs/e2109d93/tmp/one17.switches)
SWH=${SW/HEADING_TIE:1.5/HEADING_TIE:12.0}
MKSRC=src/w-tiny/main.cpp python3 tools/mkbots.py "ty_st1h12=$SWH,TR_STALL_ROUNDS:1" 2>&1 | tail -1
grep -n "constexpr int TR_STALL_ROUNDS\|constexpr double HEADING_TIE " bots/ty_st1h12/main.cpp
