#!/bin/bash
# stack10 final build: copy the final stack9 bot, apply the lnt / utab edits (exp/cand-stack10/apply.js), make the all-off identity copy
# (bot-off: LNT_ON and UTAB_ON false) and the PROFILE copy (bot-prof), and syntax-check all three.
set -e
cd "$(dirname "$0")/../.."
rm -rf exp/cand-stack10/bot exp/cand-stack10/bot-off exp/cand-stack10/bot-prof
cp -R exp/cand-stack9/bot exp/cand-stack10/bot
cp -R exp/cand-stack9/bot exp/cand-stack10/bot-off
node exp/cand-stack10/apply.js exp/cand-stack10/bot
node exp/cand-stack10/apply.js exp/cand-stack10/bot-off --off
cp -R exp/cand-stack10/bot exp/cand-stack10/bot-prof
sed -i '' 's/^constexpr bool PROFILE = false;/constexpr bool PROFILE = true; /' exp/cand-stack10/bot-prof/params.hpp
grep -q '^constexpr bool PROFILE = true;' exp/cand-stack10/bot-prof/params.hpp
for d in bot bot-off bot-prof; do (cd exp/cand-stack10/$d && clang++ -std=c++20 -Wall -Wextra -fsyntax-only *.cpp); done
diff -r exp/cand-stack9/bot exp/cand-stack10/bot > exp/cand-stack10/bot.diff || true
echo "built from $(md5 -q exp/cand-stack9/bot/plan.cpp) (stack9 plan.cpp); $(wc -l < exp/cand-stack10/bot.diff) diff lines"
