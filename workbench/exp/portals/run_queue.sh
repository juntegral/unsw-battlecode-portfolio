#!/bin/zsh
# exp/portals: wait until no screen eval of ours runs, then screen the given variants in order (run_screen.sh)
cd "$(dirname "$0")/../.."
while pgrep -f "eval.js --bot exp/portals/var" > /dev/null; do sleep 15; done
exec exp/portals/run_screen.sh "$@"
