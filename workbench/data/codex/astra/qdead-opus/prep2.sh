cd ~/meow-redteam/solo
mv runs/qd_base runs/qd_v1base
mv runs/qd_on runs/qd_v1on
rm -f "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/qdead-opus/scan-qd_base.jsonl" "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/qdead-opus/scan-qd_on.jsonl"
SW=$(cat "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/seen/one14.switches")
export MKSRC=src/w-qdead/main.cpp
python3 tools/mkbots.py "qd_off=" "qd_base=$SW,QUEEN_HOLD_LEN:4,QDK_TRACE:true" "qd_on=$SW,QUEEN_HOLD_LEN:4,QUEEN_DEAD_KNOWN:8,QDK_TRACE:true" "qd_dk=$SW,QUEEN_DEAD_KNOWN:8,QDK_TRACE:true" "qd_live=$SW" "qd_go=$SW,QUEEN_HOLD_LEN:4,QUEEN_DEAD_KNOWN:8"
shasum bots/qd_off/bot bots/qd_live/bot bots/mNps/bot bots/qd_go/bot
