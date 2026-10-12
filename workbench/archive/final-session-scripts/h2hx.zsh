#!/bin/zsh
# Stop the head to head on the one14 base (neutral after 37 games). Build mX15 = one15 + QUEEN_ONE_EXIT 4 from the qexit
# builder's source, check that source's all-off and one15 hashes, and start the head to head against the live bot mD15.
T=~/.claude/jobs/e2109d93/tmp
python3 $T/killtree.py "zsh $T/h2h15.zsh"
cd ~/meow-redteam/solo || exit 1
SW=$(cat $T/one15.switches)
MKSRC=src/w-qexit/main.cpp python3 tools/mkbots.py "mXoff=" 2>&1 | tail -n 1
MKSRC=src/w-qexit/main.cpp python3 tools/mkbots.py "mXliv=$SW" 2>&1 | tail -n 1
MKSRC=src/w-qexit/main.cpp python3 tools/mkbots.py "mX15=$SW,QUEEN_ONE_EXIT:4" 2>&1 | tail -n 1
shasum bots/mXoff/bot bots/mXliv/bot bots/mD15/bot bots/mX15/bot | cut -c1-12,41-
sed 's/mNps/mD15/g; s/_v14/_v15/g; s/h2h_mD15_v13/h2h_mNps_v13/; s/h2h15-done/h2h16-done/; s/H2H_P:-6/H2H_P:-8/' $T/h2h15.zsh > $T/h2h16.zsh
grep -n "mNps\|mD15" $T/h2h16.zsh | cut -c1-120
nohup zsh $T/h2h16.zsh mX15 > $T/h2h16.out 2>&1 &
sleep 1; pgrep -fl "tmp/h2h1" | cut -c1-100
date "+%H:%M:%S"
