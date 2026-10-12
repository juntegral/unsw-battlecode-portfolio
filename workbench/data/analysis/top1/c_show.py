#!/usr/bin/env python3
"""c_show.py: print the compact per-game tables of c_build.py for a list of games, to read them before they go into the report.

usage: python3 c_show.py <step> <r1> <r2> <game_id> [<game_id> ...]
Each table also gets a line of sums over the rows shown (pearls, splits, deaths), so that the text can quote totals.
"""
import json
import os
import sys

sys.dont_write_bytecode = True
from c_build import table  # noqa: E402

step, r1, r2 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
for gid in sys.argv[4:]:
    print("\n".join(table(gid, step, r1, r2)))
    blocks = {}
    for path, lo, hi in ((f"c_out/ec_{gid}_0_150.json", 0, 149), (f"c_out/ec_{gid}_150_350.json", 150, 349)):
        if os.path.exists(path):
            d = json.load(open(path))
            for r, row in d["blocks"].items():
                if lo <= int(r) <= hi and r1 <= int(r) <= r2:
                    blocks[int(r)] = row
    keys = ["nat", "corpse_own", "corpse_enemy", "split", "rammed", "rammer", "boxed", "freedeath", "nat_hot_own", "nat_hot_enemy"]
    for s in "AB":
        print(f"  sums {s} r{r1}-{r2}: " + ", ".join(f"{k} {sum(b[s].get(k, 0) for b in blocks.values())}" for k in keys))
    print()
