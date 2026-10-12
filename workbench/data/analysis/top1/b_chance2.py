#!/usr/bin/env python3
"""b_chance2.py <team_id>: finer tables of the team's in-view ram chances on the enemy queen (sub-session A2).

Same data as b_chance.py (q3v2, 2000+ opponents, no Schooltime, in-view only). Tables:
  1. attacker 2-3 long: taken by round bucket and by (attacker length, her length)
  2. "trade test": taken by whether her length >= attacker length, >= attacker length - 1, by round bucket
  3. taken by number of chances the same dragon already had on her in the 5 rounds before (a follower that keeps
     getting chances) and whether the same dragon took a later chance
  4. per game: games with at least one in-view chance not taken, and how those games ended
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
tid = sys.argv[1]
games = {g["game_id"]: g for g in csv.DictReader(open(os.path.join(HERE, "games.csv")))}
rows = []
for gid, g in games.items():
    if g["map"] == "Schooltime":
        continue
    side = "A" if g["teamAId"] == tid else "B" if g["teamBId"] == tid else None
    if side is None:
        continue
    op = "B" if side == "A" else "A"
    try:
        if float(g["team%sElo" % op]) < 2000:
            continue
    except ValueError:
        continue
    p = os.path.join(HERE, "q3v2", gid + ".json")
    if not os.path.exists(p):
        continue
    q = json.load(open(os.path.join(HERE, "q", gid + ".json")))
    ed = q["sides"][op].get("qdeath")
    for c in json.load(open(p))["chances"]:
        if c[1] != side or not c[9]:
            continue
        r, _, did, ln, st, tk, hl, lg, oqa, inv = c
        free = -(-ln // 4)
        rows.append(dict(gid=gid, map=g["map"], size=g["map_size"], r=r, id=did, len=ln, steps=st, taken=tk, her=hl, longest=lg, oqa=oqa,
                         cost=max(0, st - free), win=g["winner"] == side, her_death=ed["round"] if ed else None,
                         her_rammed=bool(ed and ed.get("reason") == "headon")))


def show(name, key, sel=lambda x: True):
    c = defaultdict(lambda: [0, 0])
    for x in rows:
        if sel(x):
            k = key(x)
            c[k][0] += x["taken"]
            c[k][1] += 1
    print(f"  {name}: " + " | ".join(f"{k}: {v[0]}/{v[1]}" for k, v in sorted(c.items(), key=lambda kv: str(kv[0]))))


def rb(r):
    return "r000-049" if r < 50 else "r050-099" if r < 100 else "r100-199" if r < 200 else "r200+"


print(f"team {tid}: {len(rows)} in-view chances")
show("1a. attacker 2 long, by round", lambda x: rb(x["r"]), lambda x: x["len"] == 2)
show("1b. attacker 3 long, by round", lambda x: rb(x["r"]), lambda x: x["len"] == 3)
show("1c. attacker 2-3 long, her length >= attacker, by round", lambda x: rb(x["r"]), lambda x: x["len"] <= 3 and x["her"] >= x["len"])
show("1d. attacker 3 long, her 2 long, by cost", lambda x: "cost %d" % x["cost"], lambda x: x["len"] == 3 and x["her"] == 2)
show("1e. attacker 3 long, her 2 long, by round", lambda x: rb(x["r"]), lambda x: x["len"] == 3 and x["her"] == 2)
show("2a. her length >= attacker length", lambda x: "all rounds")
show("2a. her length >= attacker length", lambda x: rb(x["r"]), lambda x: x["her"] >= x["len"])
show("2b. her length = attacker length - 1", lambda x: rb(x["r"]), lambda x: x["her"] == x["len"] - 1)
show("2c. her length <= attacker length - 2", lambda x: rb(x["r"]), lambda x: x["her"] <= x["len"] - 2)
show("2d. her length >= attacker length, by own queen alive", lambda x: "own queen alive %d" % x["oqa"], lambda x: x["her"] >= x["len"])
show("2e. her length >= attacker length, by map size", lambda x: x["size"], lambda x: x["her"] >= x["len"])
show("2f. her length >= attacker length, by cost", lambda x: "cost %d" % x["cost"], lambda x: x["her"] >= x["len"])
show("2g. her length >= attacker length, r100+, by attacker length", lambda x: "L%d" % x["len"], lambda x: x["her"] >= x["len"] and x["r"] >= 100)
show("2h. her length >= attacker length, r0-99, by attacker length", lambda x: "L%d" % x["len"], lambda x: x["her"] >= x["len"] and x["r"] < 100)
show("2i. her length < attacker length, by (attacker, her)", lambda x: "L%d vs %d" % (min(x["len"], 5), min(x["her"], 5)), lambda x: x["her"] < x["len"])
# repeated chances by the same dragon
by = defaultdict(list)
for x in rows:
    by[(x["gid"], x["id"])].append(x)
streak = Counter()
later = Counter()
for k, lst in by.items():
    lst.sort(key=lambda x: x["r"])
    nt = [x for x in lst if not x["taken"]]
    if nt:
        streak[min(len(nt), 5)] += 1
        later["this dragon rammed her later" if any(x["taken"] for x in lst) else "never"] += 1
print("  3. dragons with at least one in-view chance not taken:", sum(streak.values()), "| by number of such turns:", dict(sorted(streak.items())), "|", dict(later))
# per game
pg = defaultdict(lambda: [0, 0, None, None])
for x in rows:
    v = pg[x["gid"]]
    v[0] += 1
    v[1] += x["taken"]
    v[2] = x["win"]
    v[3] = (x["her_death"], x["her_rammed"])
some = [g for g, v in pg.items() if v[1] < v[0]]
never = [g for g in some if not pg[g][3][1]]
print(f"  4. games with an in-view chance: {len(pg)}; with at least one not taken: {len(some)}; of those, games in which her queen was never rammed: {len(never)} (won {sum(1 for g in never if pg[g][2])})")
print(f"     games with an in-view chance and none missed: {len(pg) - len(some)} (won {sum(1 for g, v in pg.items() if v[1] == v[0] and v[2])})")
print(f"     games with a missed one where she was rammed later anyway: {len(some) - len(never)} (won {sum(1 for g in some if pg[g][3][1] and pg[g][2])})")
