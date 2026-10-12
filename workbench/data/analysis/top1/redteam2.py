#!/usr/bin/env python3
"""More attacks on H1 (queen hunt). Reads q/*.json, sealed map excluded.

T1  Same opponents: queen-kill rate against test4 (19) and WeHaveQuizzes (87), the two teams that make up most of our
    2000+ sample, by the top three and by us.
T2  Close approaches only (the attacker got within 2 steps of the queen): kill rate, top three vs us, by length.
T3  Our own games: win rate by whether we rammed their queen, split by economy at round 150 and by our queen's fate.
T4  Our kills: which of our dragons rammed her (length), and what the game became.
T5  How often the enemy queen died of something else against us vs against the top three (do we need to kill her at all?).
"""
import glob
import json
from collections import Counter, defaultdict

TOP3 = {306, 91, 264}
SEALED = {"Schooltime"}
games = [d for d in (json.load(open(f)) for f in glob.glob("q/*.json")) if d["map"] not in SEALED]


def size(d):
    c = d["w"] * d["h"]
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


def qkill(d, by, of):
    qd = d["sides"][of]["qdeath"]
    return qd["round"] if qd and qd["reason"] == "headon" and qd["killer"] and qd["killer"]["team"] == by else None


def at(lst, r):
    return lst[min(r, len(lst) - 1)]


print("=== T1. rams on the queen of the same opponent: kills / games (and that opponent's queen alive at the end)")
tab = defaultdict(lambda: [0, 0, 0])
for d in games:
    for s in "AB":
        o = "B" if s == "A" else "A"
        att, vic = d["sides"][s]["team"], d["sides"][o]["team"]
        if vic not in (19, 87):
            continue
        grp = "top three" if att in TOP3 else "meow" if att == 1119 else None
        if not grp:
            continue
        for key in ((vic, size(d), grp), (vic, "all", grp)):
            t = tab[key]
            t[0] += 1
            t[1] += qkill(d, s, o) is not None
            t[2] += d["sides"][o]["final"]["queen"] > 0
for k, v in sorted(tab.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
    print(f"  vs team {k[0]:3d} {k[1]:6s} {k[2]:9s} games {v[0]:3d} kills/game {v[1] / v[0]:.2f}  her queen alive at end {v[2] / v[0]:.2f}")

print("\n=== T2. approaches in which the attacker got within 2 steps of the queen")
tab = defaultdict(lambda: [0, 0])
for d in games:
    for s in "AB":
        o = "B" if s == "A" else "A"
        att = d["sides"][o]["team"]
        grp = "top three" if att in TOP3 else "meow" if att == 1119 else None
        if not grp or (d["sides"][s]["elo"] or 0) < 2000:
            continue
        for ep in d["sides"][s]["episodes"]:
            if ep["min"] > 2:
                continue
            cls = "L2-3" if ep["len"] <= 3 else "L4" if ep["len"] == 4 else "L5+"
            for key in ((grp, cls, "big map" if d["w"] * d["h"] > 1200 else "map <= 1200"), (grp, cls, "any")):
                tab[key][0] += 1
                tab[key][1] += ep["outcome"] == "it_rammed" and bool(ep.get("victim_queen"))
for k, v in sorted(tab.items()):
    print(f"  {k[0]:9s} {k[1]:5s} {k[2]:12s} close approaches {v[0]:5d} rammed the queen {v[1] / v[0]:.3f}")

print("\n=== T3. OUR games (opp >= 2000): win rate by 'we rammed their queen', economy at r150, and our queen's fate")
tab = defaultdict(lambda: [0, 0])
for d in games:
    for s in "AB":
        o = "B" if s == "A" else "A"
        if d["sides"][s]["team"] != 1119 or (d["sides"][o]["elo"] or 0) < 2000 or d["rounds"] <= 150:
            continue
        a, b = at(d["sides"][s]["per"]["total"], 150), at(d["sides"][o]["per"]["total"], 150)
        if not b:
            continue
        eco = "behind" if a / b < 0.83 else "even" if a / b < 1.2 else "ahead"
        k = qkill(d, s, o) is not None
        their_dead = d["sides"][o]["qdeath"] is not None
        key = (eco, "we rammed her" if k else "she died otherwise" if their_dead else "she lived")
        tab[key][0] += d["winner"] == s
        tab[key][1] += 1
for k, v in sorted(tab.items()):
    print(f"  {k[0]:6s} {k[1]:20s} {v[0]:3d}/{v[1]:3d} = {v[0] / v[1]:.2f}")

print("\n=== T4. our kills of their queen: our dragon's length, her length, round, result")
c = Counter()
for d in games:
    for s in "AB":
        o = "B" if s == "A" else "A"
        if d["sides"][s]["team"] != 1119 or (d["sides"][o]["elo"] or 0) < 2000:
            continue
        qd = d["sides"][o]["qdeath"]
        if qkill(d, s, o) is None:
            continue
        c[("killer len", "2-3" if qd["killer"]["len"] <= 3 else "4" if qd["killer"]["len"] == 4 else "5+")] += 1
        c[("her len", "2-3" if qd["len"] <= 3 else "4-9" if qd["len"] <= 9 else "10+")] += 1
        c[("result", ("W " if d["winner"] == s else "L ") + d["end_type"])] += 1
        c[("map class", size(d))] += 1
print(" ", {f"{k[0]} {k[1]}": v for k, v in sorted(c.items())})

print("\n=== T5. how the ENEMY queen ended, share of games: against the top three (pooled) and against us")
for grp in ("top three", "meow"):
    c = Counter()
    n = 0
    for d in games:
        for s in "AB":
            o = "B" if s == "A" else "A"
            t = d["sides"][s]["team"]
            if (grp == "top three" and t not in TOP3) or (grp == "meow" and t != 1119) or (d["sides"][o]["elo"] or 0) < 2000:
                continue
            n += 1
            qd = d["sides"][o]["qdeath"]
            if qd is None:
                c["alive"] += 1
            elif qkill(d, s, o) is not None:
                c["rammed by us"] += 1
            elif qd["reason"] == "noaction":
                c["no-action (own doing)"] += 1
            else:
                c["crashed or own/ally ram"] += 1
    print(f"  {grp:9s} n={n} " + " ".join(f"{k}={v / n:.2f}" for k, v in c.most_common()))
