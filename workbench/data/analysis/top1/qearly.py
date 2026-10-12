#!/usr/bin/env python3
"""Own queen's death by map: dead before r50 / r100 / r300, cause (rammed by enemy / other = boxed), per team.
Opp elo >= 2000, Schooltime excluded. Also by the bot's own gate (cells <= 600: queen rules off unless home closed)."""
import csv
import json
from collections import defaultdict

TEAMS = {"306": "Vib", "91": "SSS", "264": "forgot", "1119": "meow"}
tab = defaultdict(lambda: defaultdict(int))
cells = {}
for g in csv.DictReader(open("games.csv")):
    if g["map"] == "Schooltime":
        continue
    q = None
    cells[g["map"]] = int(g["cells"])
    for s in "AB":
        o = "B" if s == "A" else "A"
        if g[f"team{s}Id"] not in TEAMS or not g[f"team{o}Elo"] or float(g[f"team{o}Elo"]) < 2000:
            continue
        if q is None:
            q = json.load(open(f"q/{g['game_id']}.json"))
        me = q["sides"][s]
        qd = me["qdeath"]
        name = TEAMS[g[f"team{s}Id"]]
        for key in (g["map"], "cells<=600" if int(g["cells"]) <= 600 else "cells 601-1500" if int(g["cells"]) <= 1500 else "cells>1500", "ALL"):
            t = tab[(key, name)]
            t["n"] += 1
            t["won"] += g["winner"] == s
            if qd:
                rammed = qd["reason"] == "headon" and qd["killer"] and qd["killer"]["team"] == o
                r = qd["round"]
                for lim in (50, 100, 300):
                    if r < lim:
                        t[f"d{lim}"] += 1
                        t[f"d{lim}ram"] += bool(rammed)
                t["dead"] += 1
                t["ram"] += bool(rammed)
                t["qlen_at_death"] += qd.get("length", 0) or 0
print("map (cells) | team: games, wins | queen dead before r50 (rammed) | before r100 (rammed) | before r300 (rammed) | dead by end (rammed)")
keys = ["ALL", "cells<=600", "cells 601-1500", "cells>1500"] + sorted(cells, key=lambda m: cells[m])
for key in keys:
    print(f"--- {key} {cells.get(key, '')}")
    for name in ("meow", "Vib", "SSS", "forgot"):
        t = tab[(key, name)]
        n = t["n"]
        if not n:
            continue
        print(f"   {name:6s} n={n:3d} won {100 * t['won'] / n:3.0f}% | r50 {100 * t['d50'] / n:3.0f}% ({t['d50ram']}/{t['d50']}) | r100 {100 * t['d100'] / n:3.0f}% ({t['d100ram']}/{t['d100']}) | "
              f"r300 {100 * t['d300'] / n:3.0f}% ({t['d300ram']}/{t['d300']}) | end {100 * t['dead'] / n:3.0f}% ({t['ram']}/{t['dead']})")
