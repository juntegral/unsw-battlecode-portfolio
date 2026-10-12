#!/usr/bin/env python3
"""Checks used to attack the hypotheses (reads q/*.json, q2/*.json). Sealed-queen map (Schooltime) excluded.

R1  Does killing the enemy queen separate wins from losses once the economy is held equal?
    Games of the three top teams (opp elo >= 2000). "Even" = total lengths within 20% of each other at round 150.
R2  Is the kill a consequence of already winning? Total-length ratio (killer team / victim team) at the round of the kill.
R3  Kill rate against opponents of different strength (does a top team kill queens only of weaker teams?).
R4  Our side: what share of rounds was their queen within one-turn reach of one of OUR heads, split by the map-size
    switch in our trade rule (aggressive mode <= 1200 cells), and how often did we ram her then.
R5  Escort check: among top-team queens with a small enemy (<= 4 long) within 3 steps at round start, does having an
    ally head within 3 steps change the chance she is rammed in the next 5 rounds?
R6  Timing of our queen's death vs their queen's death in our games (who loses the queen first).
"""
import glob
import json
import statistics
from collections import Counter, defaultdict

TOP3 = {306: "Vibing++", 91: "SSS", 264: "forgot"}
SEALED = {"Schooltime"}
Q = {}
for f in glob.glob("q/*.json"):
    d = json.load(open(f))
    Q[d["game_id"]] = d


def size(d):
    c = d["w"] * d["h"]
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


def sides(team, min_elo=2000):
    for d in Q.values():
        if d["map"] in SEALED:
            continue
        for s in "AB":
            o = "B" if s == "A" else "A"
            if d["sides"][s]["team"] == team and (d["sides"][o]["elo"] or 0) >= min_elo:
                yield d, s, o


def qkill(d, by, of):
    """Round at which side `by` rammed the queen of side `of`, else None."""
    qd = d["sides"][of]["qdeath"]
    if qd and qd["reason"] == "headon" and qd["killer"] and qd["killer"]["team"] == by:
        return qd["round"]
    return None


def at(lst, r):
    return lst[min(r, len(lst) - 1)]


print("=== R1. win rate by 'we rammed their queen', economy held even at round 150 (top three pooled; each game counted from each top team's side)")
for sz in ("small", "medium", "large", "all"):
    for label, lo, hi in (("behind at r150 (<0.83)", 0, 0.83), ("even at r150 (0.83-1.2)", 0.83, 1.2), ("ahead at r150 (>1.2)", 1.2, 99)):
        tab = defaultdict(lambda: [0, 0])
        for team in TOP3:
            for d, s, o in sides(team):
                if sz != "all" and size(d) != sz:
                    continue
                if d["rounds"] <= 150:
                    continue
                a, b = at(d["sides"][s]["per"]["total"], 150), at(d["sides"][o]["per"]["total"], 150)
                if not b:
                    continue
                ratio = a / b
                if not (lo <= ratio < hi):
                    continue
                k = qkill(d, s, o)
                lost = qkill(d, o, s)
                key = ("killed theirs" if k is not None else "did not") + " / " + ("lost ours to a ram" if lost is not None else "kept ours from rams")
                tab[key][0] += d["winner"] == s
                tab[key][1] += 1
        print(f"  {sz:6s} {label:24s} " + " | ".join(f"{k}: {v[0]}/{v[1]}={v[0] / v[1]:.2f}" for k, v in sorted(tab.items())))

print("\n=== R1b. the same, only kills BEFORE round 200 vs no kill before round 200, games that were even at the kill horizon (r150)")
tab = defaultdict(lambda: [0, 0])
for team in TOP3:
    for d, s, o in sides(team):
        if d["rounds"] <= 200:
            continue
        a, b = at(d["sides"][s]["per"]["total"], 150), at(d["sides"][o]["per"]["total"], 150)
        if not b or not (0.83 <= a / b < 1.2):
            continue
        k = qkill(d, s, o)
        lost = qkill(d, o, s)
        key = ("early kill" if k is not None and k < 200 else "no early kill") + " / " + ("lost ours early" if lost is not None and lost < 200 else "ours alive at r200")
        tab[(size(d), key)][0] += d["winner"] == s
        tab[(size(d), key)][1] += 1
for k, v in sorted(tab.items()):
    print(f"  {k[0]:6s} {k[1]:45s} {v[0]}/{v[1]} = {v[0] / v[1]:.2f}")

print("\n=== R2. economy at the moment of the kill: total length of the killer's team / victim's team (top three as killers)")
for sz in ("small", "medium", "large"):
    ratios = []
    for team in TOP3:
        for d, s, o in sides(team):
            if size(d) != sz:
                continue
            k = qkill(d, s, o)
            if k is None:
                continue
            a, b = at(d["sides"][s]["per"]["total"], k), at(d["sides"][o]["per"]["total"], k)
            if b:
                ratios.append(a / b)
    ratios.sort()
    n = len(ratios)
    print(f"  {sz:6s} n={n} median {statistics.median(ratios):.2f}; killer's team behind (<0.9): {sum(r < 0.9 for r in ratios) / n:.2f}, "
          f"about even (0.9-1.1): {sum(0.9 <= r <= 1.1 for r in ratios) / n:.2f}, ahead (>1.1): {sum(r > 1.1 for r in ratios) / n:.2f}")

print("\n=== R3. queen-kill rate of the top three by opponent (rams on the enemy queen per game)")
by = defaultdict(lambda: [0, 0])
for team in TOP3:
    for d, s, o in sides(team, 0):
        opp = d["sides"][o]
        grp = "vs another top-3 team" if opp["team"] in TOP3 else "vs meow" if opp["team"] == 1119 else "vs elo>=2150" if (opp["elo"] or 0) >= 2150 else "vs elo 2000-2150" if (opp["elo"] or 0) >= 2000 else "vs elo<2000"
        by[(size(d), grp)][0] += qkill(d, s, o) is not None
        by[(size(d), grp)][1] += 1
for k, v in sorted(by.items()):
    print(f"  {k[0]:6s} {k[1]:24s} {v[0]}/{v[1]} = {v[0] / v[1]:.2f}")

print("\n=== R4. their queen within one-turn reach of one of our heads: share of her rounds and rams per 1000 such rounds, by our trade mode")
for team, name in list(TOP3.items()) + [(1119, "meow")]:
    for mode in ("<=1200 cells", ">1200 cells"):
        rounds = exp = ram_exp = games = kills = 0
        for d, s, o in sides(team):
            if (d["w"] * d["h"] <= 1200) != (mode == "<=1200 cells"):
                continue
            games += 1
            k = qkill(d, s, o)
            kills += k is not None
            for r, x in enumerate(d["sides"][o]["per"]["q"]):
                if not x or r < 20:
                    continue
                rounds += 1
                if x[9] is not None and x[9] <= 0:
                    exp += 1
                    ram_exp += k == r
        print(f"  {name:9s} {mode:13s} games={games:3d} kills/game={kills / max(1, games):.2f} reach-rounds/game={exp / max(1, games):5.1f} "
              f"({exp / max(1, rounds):.3f} of her rounds) rams per 1000 reach-rounds={1000 * ram_exp / max(1, exp):.0f}")

print("\n=== R5. escort check (top-three queens, own side): small enemy within 3 steps at round start; rammed within the next 5 rounds?")
tab = defaultdict(lambda: [0, 0])
for team in list(TOP3) + [1119]:
    for d, s, o in sides(team):
        sd = d["sides"][s]
        qd = sd["qdeath"]
        ram = qd["round"] if qd and qd["reason"] == "headon" and qd["killer"] and qd["killer"]["team"] == o else -99
        q = sd["per"]["q"]
        for r, x in enumerate(q):
            if not x or x[10] is None or x[10] > 3:
                continue
            key = ("meow" if team == 1119 else "top3", "ally within 3" if x[7] >= 1 else "no ally within 3", "queen len>=5" if x[2] >= 5 else "queen len<=4")
            tab[key][0] += r <= ram <= r + 4
            tab[key][1] += 1
for k, v in sorted(tab.items()):
    print(f"  {k[0]:5s} {k[1]:17s} {k[2]:13s} rammed within 5 rounds: {v[0]}/{v[1]} = {v[0] / v[1]:.3f}")

print("\n=== R6. our games: which queen dies first (any cause), non-sealed, opp >= 2000")
c = Counter()
for d, s, o in sides(1119):
    a, b = d["sides"][s]["qdeath"], d["sides"][o]["qdeath"]
    ra = a["round"] if a else 999
    rb = b["round"] if b else 999
    c["ours first" if ra < rb else "theirs first" if rb < ra else "neither/same"] += 1
    if a and not b:
        c["ours died, theirs never"] += 1
    if b and not a:
        c["theirs died, ours never"] += 1
print(" ", dict(c))
