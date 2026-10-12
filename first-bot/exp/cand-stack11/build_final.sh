#!/bin/bash
# stack11 final build: copy the final stack10 bot, apply the gh / kx / lwk edits (exp/cand-stack11/apply.js), make the all-off identity copy
# (bot-off: GH_ON, KX_ON and LWK_ON false) and the PROFILE copy (bot-prof), and syntax-check all three.
set -e
cd "$(dirname "$0")/../.."
rm -rf exp/cand-stack11/bot exp/cand-stack11/bot-off exp/cand-stack11/bot-prof
cp -R exp/cand-stack10/bot exp/cand-stack11/bot
cp -R exp/cand-stack10/bot exp/cand-stack11/bot-off
node exp/cand-stack11/apply.js exp/cand-stack11/bot
node exp/cand-stack11/apply.js exp/cand-stack11/bot-off --off
cp -R exp/cand-stack11/bot exp/cand-stack11/bot-prof
sed -i '' 's/^constexpr bool PROFILE = false;/constexpr bool PROFILE = true; /' exp/cand-stack11/bot-prof/params.hpp
grep -q '^constexpr bool PROFILE = true;' exp/cand-stack11/bot-prof/params.hpp
for d in bot bot-off bot-prof; do (cd exp/cand-stack11/$d && clang++ -std=c++20 -Wall -Wextra -fsyntax-only *.cpp); done
diff -r exp/cand-stack10/bot exp/cand-stack11/bot > exp/cand-stack11/bot.diff || true
diff -r exp/cand-stack10/bot exp/cand-stack11/bot-off > exp/cand-stack11/bot-off.diff || true
echo "built from $(md5 -q exp/cand-stack10/bot/plan.cpp) (stack10 plan.cpp) / $(md5 -q exp/cand-stack10/bot/params.hpp) (params.hpp); $(wc -l < exp/cand-stack11/bot.diff) diff lines"
