#!/bin/zsh
# qaway-opus: diff of my change on the current base, and its all-off hash.
H=${0:A:h}
S=$HOME/meow-redteam/solo
rm -f $S/src/w-qaway/main-on-current-base.cpp.orig
diff -u $S/src/solo/main.cpp $S/src/w-qaway/main-on-current-base.cpp > $H/qaway-opus-on-current-base.diff
wc -l $H/*.diff
cd $S
MKSRC=src/w-qaway/main-on-current-base.cpp python3 tools/mkbots.py "qa_cur_off="
shasum bots/qa_cur_off/bot
date
