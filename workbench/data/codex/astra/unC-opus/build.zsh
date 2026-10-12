#!/bin/zsh
# one17 without SPLIT_ROUND0 (arm uc_ns0)
S=$(cat ~/.claude/jobs/e2109d93/tmp/one17.switches)
V=${S/SPLIT_ROUND0:true,/}
cd $HOME/meow-redteam/solo
MKSRC=src/solo/main.cpp python3 tools/mkbots.py "uc_ns0=$V"
ls -la bots/uc_ns0/
