#!/bin/zsh
# exp/portals: behaviour identity on the other nine maps (tools/fingerprint.js: event-stream hash; indicators and instruction counts
# skipped). Both bots as team A against bots/proxy4_king on maps/online-20260927, seeds 1 and 2, nice 10.
#   head   exp/portals/bot-head (bot/ at the current HEAD, v1 final) vs exp/portals/bot-v11 (the module rebased onto it) -> portals.diff
#   orig   exp/portals/bot-base (bot/ at 5497983, where the module was built and measured) vs exp/portals/bot -> portals-5497983.diff
# usage: run_identity.sh head|orig <seed>   Output: exp/portals/identity/<which>-seed<seed>.txt
cd "$(dirname "$0")/../.."
mkdir -p exp/portals/identity
M=autarky,default,devil,prisoners_dilemma,queen_of_spades,schooltime,slithery_fight,trauma,trophy
case $1 in head) A=exp/portals/bot-head; B=exp/portals/bot-v11;; orig) A=exp/portals/bot-base; B=exp/portals/bot;; esac
O=exp/portals/identity/$1-seed$2.txt
nice -n 10 node tools/fingerprint.js --same $A $B --maps $M --seed $2 > $O 2>&1; echo "exit $?" >> $O
