#!/bin/bash
# stack12 final build: copy the final stack11 bot (commit 98e510a), apply the pf edits (exp/cand-stack12/apply.js), make the all-off identity copy
# (bot-off: PF_ON false) and the PROFILE copy (bot-prof), and syntax-check all three.
set -e
cd "$(dirname "$0")/../.."
rm -rf exp/cand-stack12/bot exp/cand-stack12/bot-off exp/cand-stack12/bot-prof
cp -R exp/cand-stack11/bot exp/cand-stack12/bot
cp -R exp/cand-stack11/bot exp/cand-stack12/bot-off
node exp/cand-stack12/apply.js exp/cand-stack12/bot
node exp/cand-stack12/apply.js exp/cand-stack12/bot-off --off
cp -R exp/cand-stack12/bot exp/cand-stack12/bot-prof
sed -i '' 's/^constexpr bool PROFILE = false;/constexpr bool PROFILE = true; /' exp/cand-stack12/bot-prof/params.hpp
grep -q '^constexpr bool PROFILE = true;' exp/cand-stack12/bot-prof/params.hpp
for d in bot bot-off bot-prof; do (cd exp/cand-stack12/$d && clang++ -std=c++20 -Wall -Wextra -fsyntax-only *.cpp); done
diff -r exp/cand-stack11/bot exp/cand-stack12/bot > exp/cand-stack12/bot.diff || true
diff -r exp/cand-stack11/bot exp/cand-stack12/bot-off > exp/cand-stack12/bot-off.diff || true
echo "built from $(md5 -q exp/cand-stack11/bot/plan.cpp) (stack11 plan.cpp) / $(md5 -q exp/cand-stack11/bot/params.hpp) (params.hpp); $(wc -l < exp/cand-stack12/bot.diff) diff lines"
