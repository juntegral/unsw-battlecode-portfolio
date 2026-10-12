cd ~/meow-redteam/solo
SW=$(cat ~/.claude/jobs/e2109d93/tmp/one17.switches)
(MKSRC=src/w-tiny/main.cpp python3 tools/mkbots.py "ty_ce=$SW,CRAMPED_EAT:true" 2>&1 | tail -1) &
(MKSRC=src/w-tiny/main.cpp python3 tools/mkbots.py "ty_cest1=$SW,CRAMPED_EAT:true,TR_STALL_ROUNDS:1" 2>&1 | tail -1) &
wait
