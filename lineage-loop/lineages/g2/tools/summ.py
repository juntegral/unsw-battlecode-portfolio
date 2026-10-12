#!/usr/bin/env python3
"""Summarise g2eval jsonl: per opponent win rate, per map W/L, longest diffs, our death causes."""
import sys, json, os, collections
rows = [json.loads(l) for f in sys.argv[1:] for l in open(f)]
by = collections.defaultdict(list)
for r in rows:
    side = 0 if r["A"] == r["ours"] else 1
    opp = os.path.basename(r["B"] if side == 0 else r["A"])
    res = 0.5 if r["winner"] is None else (1.0 if r["winner"] == "AB"[side] else 0.0)
    by[opp].append((r, side, res))
for opp, lst in sorted(by.items()):
    sc = sum(x[2] for x in lst)
    print(f"== vs {opp}: {sc}/{len(lst)} = {100*sc/len(lst):.0f}%")
    maps = collections.defaultdict(list)
    dcause = collections.Counter(); ocause = collections.Counter()
    for r, side, res in lst:
        maps[r["map"]].append((res, r["longest"][side] - r["longest"][1 - side], r["reason"]))
        dcause.update(r["deaths"]["AB"[side]]); ocause.update(r["deaths"]["AB"[1 - side]])
    for m, v in sorted(maps.items()):
        print(f"   {m:18s} {sum(x[0] for x in v):4.1f}/{len(v)}  longest-diff {[x[1] for x in v]}  elim {sum(1 for x in v if x[2]==0)}")
    print(f"   our deaths {dict(dcause)}  their deaths {dict(ocause)}")
