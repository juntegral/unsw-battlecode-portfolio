python3 "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/qdead-opus/patch3.py" ~/meow-redteam/solo/src/w-qdead/main.cpp
cd ~/meow-redteam/solo
SW=$(cat "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/seen/one14.switches")
export MKSRC=src/w-qdead/main.cpp
python3 tools/mkbots.py "qd_off=" "qd_base=$SW,QUEEN_HOLD_LEN:4,QDK_TRACE:true" "qd_on=$SW,QUEEN_HOLD_LEN:4,QUEEN_DEAD_KNOWN:8,QDK_TRACE:true" "qd_nf=$SW,QUEEN_HOLD_LEN:4,QUEEN_HOLD_FEED:false,QUEEN_DEAD_KNOWN:8,QDK_TRACE:true" "qd_dk=$SW,QUEEN_DEAD_KNOWN:8,QDK_TRACE:true" "qd_live=$SW"
shasum bots/qd_off/bot bots/qd_live/bot bots/mNps/bot
