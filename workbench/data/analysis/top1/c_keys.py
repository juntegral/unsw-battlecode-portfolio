#!/usr/bin/env python3
"""c_keys.py: list the per-block keys of a c_econ.py JSON file and the non-zero sums of every numeric key over the blocks.

usage: python3 c_keys.py <game_id> [r1] [r2]
"""
import json
import sys

gid = sys.argv[1]
r1 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
r2 = int(sys.argv[3]) if len(sys.argv) > 3 else 149
d = json.load(open(f"c_out/ec_{gid}_0_150.json"))
print("top-level keys:", sorted(d.keys()))
for s in "AB":
    sums = {}
    for r, row in d["blocks"].items():
        if not r1 <= int(r) <= r2:
            continue
        for k, v in row[s].items():
            if isinstance(v, (int, float)):
                sums[k] = sums.get(k, 0) + v
    print(f"side {s} ({d['names'][s]}), blocks r{r1}-{r2}:")
    print("  " + ", ".join(f"{k} {v:g}" for k, v in sorted(sums.items()) if v))
