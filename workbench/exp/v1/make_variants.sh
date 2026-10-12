#!/bin/zsh
# unsw-swarm v1: build the identity-check copies of bot/ (params.hpp flags only).
#   bot-fixoff      BELIEF_FIX_ON false, FORT_W4_ON false                           -> fortress maps must be event-identical to benchmark/
#   bot-fixoff-swf  BELIEF_FIX_ON false, FORT_W4_ON false, SWARM_AS_FORTRESS true   -> all ten maps identical to benchmark/; also the "v0 tagged" baseline
cd "$(dirname "$0")/../.."
for v in bot-fixoff bot-fixoff-swf; do
  rm -rf exp/v1/$v; cp -R bot exp/v1/$v; rm -rf exp/v1/$v/.unswbc-build
  sed -i '' 's/^constexpr bool   BELIEF_FIX_ON = true;/constexpr bool   BELIEF_FIX_ON = false;/' exp/v1/$v/params.hpp
  sed -i '' 's/^constexpr bool   FORT_W4_ON = true;/constexpr bool   FORT_W4_ON = false;/' exp/v1/$v/params.hpp
  grep -q '^constexpr bool   BELIEF_FIX_ON = false;' exp/v1/$v/params.hpp || { echo "flag edit failed ($v)"; exit 1; }
  grep -q '^constexpr bool   FORT_W4_ON = false;' exp/v1/$v/params.hpp || { echo "flag edit failed ($v w4)"; exit 1; }
done
sed -i '' 's/^constexpr bool   SWARM_AS_FORTRESS = false;/constexpr bool   SWARM_AS_FORTRESS = true;/' exp/v1/bot-fixoff-swf/params.hpp
grep -q '^constexpr bool   SWARM_AS_FORTRESS = true;' exp/v1/bot-fixoff-swf/params.hpp || { echo "flag edit failed (swf)"; exit 1; }
diff -r bot exp/v1/bot-fixoff; diff -r bot exp/v1/bot-fixoff-swf
echo built
