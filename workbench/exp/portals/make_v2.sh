#!/bin/zsh
# exp/portals v2: build the screening variants from exp/portals/bot2 (params.hpp PT2_* flags only; PLAN-v2.md)
#   w1-pocket   A1
#   w2-uroom    A1 + A2 (= bot2 defaults)
#   w3-big      A1 + A3
#   (w1-w3 ran before PT2_UROOM_KING_ONLY existed: w2's check applied to every dragon; flag it false to rebuild w2)
#   w4-kingu    A1 + A2 for the king class only (PLAN-v2.md amendment 06:45)
cd "$(dirname "$0")"
set -e
mk() { rm -rf var/$1; mkdir -p var; cp -R bot2 var/$1; }
flag() { sed -i '' "s/^constexpr $2 *$3 = [^;]*;/constexpr $2   $3 = $4;/" var/$1/params.hpp; grep -q "^constexpr $2 *$3 = $4;" var/$1/params.hpp || { echo "flag edit failed $1 $3"; exit 1; }; }
only=${1:-all}
[ $only = all -o $only = w1-pocket ] && { mk w1-pocket; flag w1-pocket bool PT2_UROOM_ON false; flag w1-pocket bool PT2_BIG_ON false; }
[ $only = all -o $only = w2-uroom ] && { mk w2-uroom; flag w2-uroom bool PT2_BIG_ON false; flag w2-uroom bool PT2_UROOM_KING_ONLY false; }
[ $only = all -o $only = w4-kingu ] && { mk w4-kingu; flag w4-kingu bool PT2_BIG_ON false; }
[ $only = all -o $only = w3-big ] && { mk w3-big; flag w3-big bool PT2_UROOM_ON false; flag w3-big bool PT2_BIG_ON true; }
for v in w1-pocket w2-uroom w3-big w4-kingu; do [ -d var/$v ] && { echo "== $v"; diff bot2/params.hpp var/$v/params.hpp | grep "^>" || true; }; done
exit 0
