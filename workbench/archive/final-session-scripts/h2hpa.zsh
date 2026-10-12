#!/bin/zsh
# Head to head of the queen-portal-ban arm (the builder's bot qbPA = one15 + QUEEN_PORTAL_ALL true) against the live bot.
# First confirm that bot's switch list differs from the live bot's by that one constant.
T=~/.claude/jobs/e2109d93/tmp
cd ~/meow-redteam/solo || exit 1
diff <(grep "^constexpr" bots/mD15/main.cpp) <(grep "^constexpr" bots/qbPA/main.cpp)
diff bots/mD15/main.cpp bots/qbPA/main.cpp | grep -c "^[<>]"
shasum bots/qbPA/bot | cut -c1-12
pgrep -f "tmp/h2h16.zsh qbPA" > /dev/null || H2H_P=8 nohup zsh $T/h2h16.zsh qbPA > $T/h2h16-qbPA.out 2>&1 &
sleep 1; pgrep -fl "tmp/h2h16" | cut -c1-90
date "+%H:%M:%S"; uptime | sed 's/.*load/load/'
