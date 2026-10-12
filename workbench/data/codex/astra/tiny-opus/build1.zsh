cd ~/meow-redteam/solo
SW=$(cat ~/.claude/jobs/e2109d93/tmp/one17.switches)
SWH=${SW/HEADING_TIE:1.5/HEADING_TIE:12.0}
(MKSRC=src/w-tiny/main.cpp python3 tools/mkbots.py "ty_17=$SW" "ty_st1=$SW,TR_STALL_ROUNDS:1" "ty_off=" 2>&1 | tail -3) &
(MKSRC=src/w-tiny/main.cpp python3 tools/mkbots.py "ty_st4=$SW,TR_STALL_ROUNDS:4" "ty_st4h12=$SWH,TR_STALL_ROUNDS:4" "ty_st2=$SW,TR_STALL_ROUNDS:2" 2>&1 | tail -3) &
wait
shasum bots/ty_off/bot bots/ty_17/bot bots/mD17/bot
cmp bots/ty_17/main.cpp bots/mD17/main.cpp && echo SOURCE_IDENTICAL_TO_mD17
cmp src/w-tiny/main.cpp src/solo/main.cpp && echo COPY_IDENTICAL_TO_BASE
