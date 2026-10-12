cd ~/meow-redteam/solo
O=$(cat ~/.claude/jobs/e2109d93/tmp/one15.switches)
export MKSRC=src/w-qbox/main.cpp
python3 tools/mkbots.py "qbA4=" "qbO15e=$O" "qbNB=$O,QUEEN_NO_BLIND_PORTAL:true"
shasum bots/qbA4/bot bots/qbO15e/bot bots/mD15/bot bots/qbNB/bot
diff -u src/solo/main.cpp src/w-qbox/main.cpp > "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/qbox-opus/qbox-opus.diff"
