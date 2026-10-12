#!/usr/bin/env python3
"""c_at.py <game_id> <round> [<round> ...]: units and total length of both sides at the given rounds (q/<id>.json),
to check per-game numbers quoted in the report. Prints side A : side B."""
import csv
import json
import sys

G = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
gid = sys.argv[1]
q = json.load(open(f"q/{gid}.json"))
g = G[gid]
print(f"{gid} {g['map']}: A = {g['teamAName']}, B = {g['teamBName']}, winner {g['winner']} by {g['end_type']}, rounds {g['rounds']}")
print("  final A : B: " + ", ".join(f"{k} {g[f'final_{f}_A']} : {g[f'final_{f}_B']}" for k, f in
                                    (("units", "units"), ("total", "total_length"), ("longest", "longest_length"), ("queen", "queen_length"))))
for r in sys.argv[2:]:
    r = int(r)
    cells = []
    for k in ("units", "total"):
        a, b = q["sides"]["A"]["per"][k], q["sides"]["B"]["per"][k]
        cells.append(f"{k} {a[r] if r < len(a) else '-'} : {b[r] if r < len(b) else '-'}")
    print(f"  r{r}: " + ", ".join(cells))
