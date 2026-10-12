cd ~/meow-redteam/solo || exit 1
V=$(cat ~/.claude/jobs/e2109d93/tmp/one17.switches)
MKSRC=src/solo/main.cpp python3 tools/mkbots.py "ud_c699=$V,CENTER_SMALL_CELLS:699" > /dev/null 2>&1
ls -la bots/ud_c699/bot
python3 "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/unD-opus/run2.py" ud_c699:un2/ud_un_center700_1.map:1
