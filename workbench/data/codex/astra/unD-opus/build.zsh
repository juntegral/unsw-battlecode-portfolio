cd ~/meow-redteam/solo || exit 1
V=$(cat ~/.claude/jobs/e2109d93/tmp/one17.switches)
MKSRC=src/solo/main.cpp python3 tools/mkbots.py "ud_q0=$V,QUEEN_MIN_CELLS:0" "ud_q624=$V,QUEEN_MIN_CELLS:624"
ls -la bots/ud_q0 bots/ud_q624
shasum bots/ud_q0/bot bots/ud_q624/bot bots/mD17/bot
