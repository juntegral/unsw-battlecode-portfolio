#!/bin/zsh
# QS_SHED_MAX (one constant + one condition): the exposed queen's "keep 2, the rest leaves as a child" split only up to that
# length; 0 = as before. Hash checks, then arms on the one16 values and their head to head against the live bot mD16.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
diff src/solo/main.cpp src/w-shed/main.cpp | grep -c "^[<>]"
SW=$(cat $T/one16.switches)
MKSRC=src/w-shed/main.cpp python3 tools/mkbots.py "mSoff=" 2>&1 | tail -n 1
MKSRC=src/w-shed/main.cpp python3 tools/mkbots.py "mSliv=$SW" 2>&1 | tail -n 1
MKSRC=src/w-shed/main.cpp python3 tools/mkbots.py "mSh1=$SW,QS_SHED_MAX:1" 2>&1 | tail -n 1
MKSRC=src/w-shed/main.cpp python3 tools/mkbots.py "mSh7=$SW,QS_SHED_MAX:7" 2>&1 | tail -n 1
shasum bots/mSoff/bot bots/mSliv/bot bots/mD16/bot bots/mSh1/bot bots/mSh7/bot | cut -c1-12,41-
sed 's/mD15/mD16/g; s/_v15/_v16/g; s/h2h16-done/h2h17-done/; s/H2H_P:-8/H2H_P:-10/' $T/h2h16.zsh > $T/h2h17.zsh
for a in mSh1 mSh7; do nohup zsh $T/h2h17.zsh $a > $T/h2h17-$a.out 2>&1 & done
sleep 1; pgrep -fl "tmp/h2h17" | cut -c1-90
date "+%H:%M:%S"
