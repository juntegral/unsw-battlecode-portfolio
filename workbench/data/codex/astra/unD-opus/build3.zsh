cd ~/meow-redteam/solo || exit 1
V=$(cat ~/.claude/jobs/e2109d93/tmp/one17.switches)
MKSRC=src/solo/main.cpp python3 tools/mkbots.py "ud_c0=$V,CENTER_SMALL_CELLS:0" > /dev/null 2>&1
ls -la bots/ud_c0/bot
U=un2/ud_un_
L=ladder/ladder_
python3 "~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/unD-opus/run3.py" \
  ud_c0:${U}center700_1.map:0:1 ud_c0:${U}queen600_1.map:0:1 ud_c0:${U}queen600_1.map:1:1 ud_c0:${U}center700_1.map:1:1 \
  ud_c0:${U}queen600_2.map:0:1 ud_c0:${U}queen600_2.map:1:1 \
  ud_c0:${L}trophy_1.map:0:1 mD17:${L}trophy_1.map:0:1 ud_c0:${L}trophy_1.map:1:1 mD17:${L}trophy_1.map:1:1 \
  mD17:${U}center700_1.map:1:2 ud_c0:${U}center700_1.map:1:2 mD17:${U}center700_1.map:0:2 ud_c0:${U}center700_1.map:0:2 \
  mD17:${U}cells4096_1.map:0:1 mD17:${U}cells4097_1.map:0:1 \
  ud_c0:${U}edgewrap_1.map:0:1 ud_c0:${U}edgewrap_1.map:1:1 \
  mD17:${U}center700_1.map:1:3 ud_c0:${U}center700_1.map:1:3 mD17:${U}center700_1.map:0:3 ud_c0:${U}center700_1.map:0:3 \
  mD17:${U}aspect_2.map:0:1 ud_c0:${U}aspect_2.map:0:1 mD17:${U}aspect_2.map:1:1 ud_c0:${U}aspect_2.map:1:1
