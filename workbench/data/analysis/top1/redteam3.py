#!/usr/bin/env python3
"""R1 again, but only games that reached round 500 (a wipe-out win kills the enemy queen by definition, which would
make 'we killed their queen -> we won' circular). Top three pooled and us; sealed map excluded; opp elo >= 2000.
Rows: own queen rammed or not; columns: we rammed theirs / she died another way / she lived.
"""
import glob
import json
from collections import defaultdict

TOP3 = {306, 91, 264}
SEALED = {"Schooltime"}
games = [d for d in (json.load(open(f)) for f in glob.glob("q/*.json")) if d["map"] not in SEALED]


def qkill(d, by, of):
    qd = d["sides"][of]["qdeath"]
    return qd is not None and qd["reason"] == "headon" and qd["killer"] is not None and qd["killer"]["team"] == by


def at(lst, r):
    return lst[min(r, len(lst) - 1)]


for grp in ("top three", "meow"):
    tab = defaultdict(lambda: [0, 0])
    n_wipe = n500 = 0
    for d in games:
        for s in "AB":
            o = "B" if s == "A" else "A"
            t = d["sides"][s]["team"]
            if (grp == "top three" and t not in TOP3) or (grp == "meow" and t != 1119) or (d["sides"][o]["elo"] or 0) < 2000:
                continue
            if d["end_type"] == "wipe-out":
                n_wipe += 1
                continue
            n500 += 1
            a, b = at(d["sides"][s]["per"]["total"], 150), at(d["sides"][o]["per"]["total"], 150)
            eco = "behind" if a / b < 0.83 else "even" if a / b < 1.2 else "ahead"
            own = "own queen dead at end" if d["sides"][s]["final"]["queen"] == 0 else "own queen alive at end"
            her = "we rammed her" if qkill(d, s, o) else "she died another way" if d["sides"][o]["final"]["queen"] == 0 else "she lived"
            for key in ((eco, own, her), ("any", own, her)):
                tab[key][0] += d["winner"] == s
                tab[key][1] += 1
    print(f"=== {grp}: round-500 games {n500} (wipe-outs left out: {n_wipe})")
    for eco in ("behind", "even", "ahead", "any"):
        for own in ("own queen dead at end", "own queen alive at end"):
            cells = []
            for her in ("we rammed her", "she died another way", "she lived"):
                v = tab.get((eco, own, her))
                if v:
                    cells.append(f"{her}: {v[0]}/{v[1]} = {v[0] / v[1]:.2f}")
            if cells:
                print(f"  r150 {eco:6s} | {own:22s} | " + " | ".join(cells))
