#!/usr/bin/env python3
"""b_rays.py: sum the sonar rays that ended on a queen's killer in the 40 rounds before the kill (sub-session A2).

Parses the b_pack.py outputs in b_out/ (pk2_<game>_<team>.txt). Each queen death by ram has a line
"killer #id team X ..." and a line "sonar rays that ended on the killer, per round: (n rays, n from a dragon that
had her in view in the last 3 rounds): r:n/m ...". Each (game, killer) is counted once.
"""
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
seen = {}
for path in sorted(glob.glob(os.path.join(HERE, "b_out", "pk2_*.txt"))):
    gid = os.path.basename(path).split("_")[1]
    killer = None
    for line in open(path):
        m = re.search(r"killer #(\d+) team ([AB])", line)
        if m:
            killer = (gid, m.group(1), m.group(2))
        if "sonar rays that ended on the killer" in line and killer:
            pairs = re.findall(r"(\d+):(\d+)/(\d+)", line.split("):", 1)[-1])
            n = sum(int(p[1]) for p in pairs)
            s = sum(int(p[2]) for p in pairs)
            seen[killer] = (n, s, len(pairs))
            killer = None
tn = ts = 0
for k, (n, s, rounds) in sorted(seen.items()):
    print(f"  game {k[0]} killer #{k[1]} (team {k[2]}): {n} rays in {rounds} rounds, {s} from a dragon that had her in view in the last 3 rounds")
    tn += n
    ts += s
print(f"total: {len(seen)} kills, {tn} rays ended on the killer in the 40 rounds before, {ts} of them from a dragon that had her in view")
