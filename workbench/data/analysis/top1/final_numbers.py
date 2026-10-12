#!/usr/bin/env python3
"""Last numbers for the report (q/*.json, opp elo >= 2000, sealed map excluded unless noted).

a. Enemy queen alive at the end, against each team, by map size.
b. Our round-500 losses with their queen alive: flips if she dies, split by whether one of our dragons ever came
   within 6 steps of her (an approach) and how many approaches there were.
c. Our approaches per game and the kills we would expect at top-three conversion rates for the same attacker lengths.
d. Kill cost: length of the dragon that rammed the enemy queen (top three), and its length class share.
"""
import glob
import json
import statistics
from collections import Counter, defaultdict

TEAMS = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}
TOP3 = {306, 91, 264}
SEALED = {"Schooltime"}
games = [json.load(open(f)) for f in glob.glob("q/*.json") if True]
games = [d for d in games if d["map"] not in SEALED]


def size(d):
    c = d["w"] * d["h"]
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


def lc(n):
    return "2" if n <= 2 else "3" if n == 3 else "4" if n == 4 else "5-6" if n <= 6 else "7-9" if n <= 9 else "10+"


def sides(team):
    for d in games:
        for s in "AB":
            o = "B" if s == "A" else "A"
            if d["sides"][s]["team"] == team and (d["sides"][o]["elo"] or 0) >= 2000:
                yield d, s, o


print("=== a. enemy queen alive at the end / own queen alive at the end, by size")
for team, name in TEAMS.items():
    line = []
    for sz in ("small", "medium", "large", "all"):
        n = e = m = 0
        for d, s, o in sides(team):
            if sz != "all" and size(d) != sz:
                continue
            n += 1
            e += d["sides"][o]["final"]["queen"] > 0
            m += d["sides"][s]["final"]["queen"] > 0
        line.append(f"{sz}: enemy {e / n:.2f} own {m / n:.2f} (n{n})")
    print(f"{name:9s} " + " | ".join(line))

print("\n=== b. our round-500 losses with their queen alive")
rate = defaultdict(lambda: [0, 0])
for team in TOP3:
    for d, s, o in sides(team):
        for ep in d["sides"][o]["episodes"]:
            k = rate[lc(ep["len"])]
            k[0] += 1
            k[1] += ep["outcome"] == "it_rammed" and bool(ep.get("victim_queen"))
conv = {k: v[1] / v[0] for k, v in rate.items()}
print("top-three kill rate per approach by attacker length:", {k: round(v, 3) for k, v in sorted(conv.items())})
tot = Counter()
exp_flip = 0.0
for d, s, o in sides(1119):
    if d["end_type"] == "wipe-out" or d["winner"] == s:
        continue
    me, op = d["sides"][s], d["sides"][o]
    mq, oq = me["final"]["queen"], op["final"]["queen"]
    if not oq:
        continue
    op_long, op_second = op["final"]["longest"], op["per"]["second"][-1]
    op_noq = op_second if oq == op_long else op_long
    flip = True if mq else me["final"]["longest"] > op_noq
    eps = op["episodes"]
    p_none = 1.0
    for ep in eps:
        p_none *= 1 - conv.get(lc(ep["len"]), 0)
    tot["games"] += 1
    tot["flip games"] += flip
    tot["flip games with >=1 approach"] += flip and len(eps) > 0
    tot["flip games with >=5 approaches"] += flip and len(eps) >= 5
    if flip:
        exp_flip += 1 - p_none
print(" ", dict(tot))
print(f"  expected flips if our approaches in those games converted at top-three rates: {exp_flip:.1f}")

print("\n=== c. our approaches and expected kills at top-three conversion")
for sz in ("small", "medium", "large", "all"):
    n = appr = kills = 0
    exp = 0.0
    games_with = 0.0
    for d, s, o in sides(1119):
        if sz != "all" and size(d) != sz:
            continue
        n += 1
        eps = d["sides"][o]["episodes"]
        appr += len(eps)
        qd = d["sides"][o]["qdeath"]
        kills += bool(qd and qd["reason"] == "headon" and qd["killer"] and qd["killer"]["team"] == s)
        p_none = 1.0
        for ep in eps:
            p_none *= 1 - conv.get(lc(ep["len"]), 0)
        games_with += 1 - p_none
    print(f"  {sz:6s} games {n:3d} approaches/game {appr / n:5.1f} our kills/game {kills / n:.2f} -> expected share of games with a kill at top-three conversion {games_with / n:.2f}")

print("\n=== d. length of the dragon that rammed the enemy queen (top three), by map size")
for sz in ("small", "medium", "large"):
    v = []
    for team in TOP3:
        for d, s, o in sides(team):
            if size(d) != sz:
                continue
            qd = d["sides"][o]["qdeath"]
            if qd and qd["reason"] == "headon" and qd["killer"] and qd["killer"]["team"] == s:
                v.append(qd["killer"]["len"])
    print(f"  {sz:6s} n={len(v)} median {statistics.median(v)} mean {sum(v) / len(v):.1f} share >=5 long {sum(x >= 5 for x in v) / len(v):.2f} share <=3 {sum(x <= 3 for x in v) / len(v):.2f}")
