#!/bin/zsh
# v1.2 checks in the coordinator's order: (a) Portals identity and (b) C2-off identity on the other maps, then (c) CPU and (d) the upload smoke
# test, then (e) the C2 sanity set. At most 3 games of ours at a time; no new game below 21 GB free (runq and cpu2 check).
cd "$(dirname "$0")/../.."
X=exp/v12
diskok() { [ "$(df -g / | awk 'NR==2 {print $4}')" -ge 21 ]; }
diskok && node exp/v11/runq.js $X/spec-ab.json --jobs 3 --cap 6 > $X/runq-ab.log 2>&1
echo done > $X/AB-DONE
diskok && exp/v11/cpu2.sh versions/v1.2/bot v12 > $X/cpu-v12.log 2>&1
# Portals CPU (the module's search) with -v
mkdir -p exp/v11/cpu-v12
(cd exp/v11/cpu-v12 && nice -n 10 ../../../tools/unswbc run ../../../maps/online-20260927/portals.map ../../../versions/v1.2/bot ../../../bots/proxy4_swarm --sandbox --seed 1 --no-logs --no-draw -o portals.replay -v 2>&1 | grep -i "points per turn\|error\|timed out" > portals-a.txt; rm -f portals.replay)
echo done > $X/CD-DONE
diskok && node exp/v11/runq.js $X/spec-e.json --jobs 3 --cap 6 > $X/runq-e.log 2>&1
echo done > $X/E-DONE
