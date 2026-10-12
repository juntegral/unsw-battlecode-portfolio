cd ~/meow-redteam/solo
SW=$(cat "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/seen/one14.switches")
export MKSRC=src/w-qdead/main.cpp
python3 tools/mkbots.py "qd_off=" "qd_base=$SW,QUEEN_HOLD_LEN:4,QDK_TRACE:true" "qd_on=$SW,QUEEN_HOLD_LEN:4,QUEEN_DEAD_KNOWN:8,QDK_TRACE:true" "qd_dk=$SW,QUEEN_DEAD_KNOWN:8,QDK_TRACE:true" "qd_live=$SW" "qd_go=$SW,QUEEN_HOLD_LEN:4,QUEEN_DEAD_KNOWN:8"
shasum bots/qd_off/bot bots/qd_live/bot bots/mNps/bot bots/qd_go/bot
awk -F'\t' '$5>=288 && $5<=1100 {print $1, $2, $5, $6, $7}' ~/meow-redteam/maps/gx/INDEX.tsv
