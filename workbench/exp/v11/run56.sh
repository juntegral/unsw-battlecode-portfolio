#!/bin/zsh
# v1.1 with C2 (spec5), its CPU and smoke test, then the v1.1b candidate with C2 (spec6) and its CPU and smoke test; stops launching below 21 GB free.
cd "$(dirname "$0")/../.."
X=exp/v11
diskok() { [ "$(df -g / | awk 'NR==2 {print $4}')" -ge 21 ]; }
diskok && node $X/runq.js $X/spec5.json --jobs 3 --cap 6 > $X/runq5.log 2>&1
diskok && $X/cpu2.sh versions/v1.1/bot v11c > $X/cpu-v11c.log 2>&1
echo done > $X/SPEC5-DONE
diskok && node $X/runq.js $X/spec6.json --jobs 3 --cap 6 > $X/runq6.log 2>&1
diskok && $X/cpu2.sh exp/v11/bot-v11b v11bc > $X/cpu-v11bc.log 2>&1
echo done > $X/SPEC6-DONE
