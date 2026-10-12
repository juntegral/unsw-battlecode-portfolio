#!/usr/bin/env python3
"""Controls for the approach result (kill rate per approach by attacker length). Reads q/*.json, sealed map excluded.

C1  only short queens (<= 4 long when the approach began) and only before round 300
C2  only games between two of the top three
C3  by number of allied heads within 6 steps of the queen when the approach began (0, 1-2, 3+)
C4  attackers of every team in the collected top-team games, by map (is the length effect on every map?)
C5  our own approaches by round phase and whether our queen was already dead
"""
import glob
import json
from collections import defaultdict

TOP3 = {306, 91, 264}
SEALED = {"Schooltime"}
games = [json.load(open(f)) for f in glob.glob("q/*.json")]


def lc(n):
    return "L2-3" if n <= 3 else "L4" if n == 4 else "L5-9" if n <= 9 else "L10+"


def kill(ep):
    return ep["outcome"] == "it_rammed" and bool(ep.get("victim_queen"))


def show(title, tab, order=None):
    print(title)
    for key in (order or sorted(tab)):
        t = tab.get(key)
        if t and t[0] >= 10:
            print(f"   {str(key):44s} approaches {t[0]:5d}  rammed the queen {t[1] / t[0]:.3f} ({t[1]})")


c1 = defaultdict(lambda: [0, 0])
c2 = defaultdict(lambda: [0, 0])
c3 = defaultdict(lambda: [0, 0])
c4 = defaultdict(lambda: [0, 0])
c5 = defaultdict(lambda: [0, 0])
for d in games:
    if d["map"] in SEALED:
        continue
    top_game = "top1" in d["sources"]
    for s in "AB":
        o = "B" if s == "A" else "A"
        att, vic = d["sides"][o]["team"], d["sides"][s]["team"]
        own_qd = d["sides"][o]["qdeath"]
        for ep in d["sides"][s]["episodes"]:
            k = kill(ep)
            cls = lc(ep["len"])
            if att in TOP3 and (d["sides"][s]["elo"] or 0) >= 2000:
                if ep["qlen"] <= 4 and ep["start"] < 300:
                    c1[cls][0] += 1
                    c1[cls][1] += k
                if vic in TOP3:
                    c2[cls][0] += 1
                    c2[cls][1] += k
                a = ep.get("a6") or 0
                key = (cls, "0 allies" if a == 0 else "1-2 allies" if a <= 2 else "3+ allies")
                c3[key][0] += 1
                c3[key][1] += k
            if top_game:
                key = (d["map"], "L5-9" if 5 <= ep["len"] <= 9 else "L2-4" if ep["len"] <= 4 else "L10+")
                c4[key][0] += 1
                c4[key][1] += k
            if att == 1119 and (d["sides"][s]["elo"] or 0) >= 2000:
                ph = "r<150" if ep["start"] < 150 else "r150-299" if ep["start"] < 300 else "r300+"
                dead = own_qd is not None and own_qd["round"] < ep["start"]
                key = (ph, "our queen dead" if dead else "our queen alive", "big map" if d["w"] * d["h"] > 1200 else "map <= 1200")
                c5[key][0] += 1
                c5[key][1] += k
show("C1 top-three attackers, queen <= 4 long, before round 300:", c1, ["L2-3", "L4", "L5-9", "L10+"])
show("C2 top-three attackers vs a top-three queen:", c2, ["L2-3", "L4", "L5-9", "L10+"])
show("C3 top-three attackers, by allied heads near the queen at the start:", c3)
print("C4 all attackers in top-team games, by map: L2-4 vs L5-9")
for m in sorted({k[0] for k in c4}):
    a, b = c4.get((m, "L2-4"), [0, 0]), c4.get((m, "L5-9"), [0, 0])
    if a[0] and b[0] >= 5:
        print(f"   {m:18s} L2-4 {a[1]:4d}/{a[0]:5d} = {a[1] / a[0]:.3f}   L5-9 {b[1]:3d}/{b[0]:4d} = {b[1] / b[0]:.3f}")
show("C5 our own approaches (meow attacking), by phase / our queen / map class:", c5)
