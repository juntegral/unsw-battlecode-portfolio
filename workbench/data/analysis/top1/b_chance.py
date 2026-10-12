#!/usr/bin/env python3
"""b_chance.py <team_id> [list]: the team's in-view ram chances on the enemy queen over all games (sub-session A2).

Reads q3v2/<game>.json for every game of the team against a 2000+ team (Schooltime left out). A chance is one turn
of one dragon: [round, side, id, length, steps needed, taken, her length, attacker is its team's longest, own queen
alive, her head in the attacker's 7x7 view]. Only chances with the view flag set are used here.
Prints cross-tables of taken / not taken by: attacker length, cost (steps beyond the free ones), steps, her length,
attacker length minus her length, own queen alive, longest, round. With "list" as second argument it also prints
every not-taken in-view chance (game, round, id, length, steps, cost, her length).
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
tid = sys.argv[1]
want_list = len(sys.argv) > 2 and sys.argv[2] == "list"
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
    for c in json.load(open(p))["chances"]:
        if c[1] != side or not c[9]:
            continue
        r, _, did, ln, st, tk, hl, lg, oqa, inv = c
        free = -(-ln // 4)
        rows.append(dict(gid=gid, map=g["map"], r=r, id=did, len=ln, steps=st, taken=tk, her=hl, longest=lg, oqa=oqa,
                         cost=max(0, st - free), free=free))
print(f"team {tid}: {len(rows)} in-view chances, taken {sum(x['taken'] for x in rows)}")


def tab(name, key, order=None):
    c = defaultdict(lambda: [0, 0])
    for x in rows:
        k = key(x)
        c[k][0] += x["taken"]
        c[k][1] += 1
    keys = order or sorted(c)
    print(f"  by {name}: " + " | ".join(f"{k}: {c[k][0]}/{c[k][1]}" for k in keys if k in c))


def lcls(n):
    return "2" if n == 2 else "3" if n == 3 else "4" if n == 4 else "5-6" if n <= 6 else "7-9" if n <= 9 else "10-12"


tab("attacker length", lambda x: x["len"])
tab("cost (paid steps)", lambda x: min(x["cost"], 5))
tab("steps needed", lambda x: min(x["steps"], 7))
tab("her length", lambda x: "2" if x["her"] == 2 else "3" if x["her"] == 3 else "4" if x["her"] == 4 else "5-9" if x["her"] <= 9 else "10-19" if x["her"] <= 19 else "20+",
    ["2", "3", "4", "5-9", "10-19", "20+"])
tab("attacker length minus her length", lambda x: max(-3, min(6, x["len"] - x["her"])))
tab("length left after paying, minus her length", lambda x: max(-3, min(6, x["len"] - x["cost"] - x["her"])))
tab("own queen alive", lambda x: x["oqa"])
tab("attacker is the team's longest", lambda x: x["longest"])
tab("round", lambda x: min(4, x["r"] // 100) * 100)
print("  by attacker length class x cost:")
for cl in ("2", "3", "4", "5-6", "7-9", "10-12"):
    c = defaultdict(lambda: [0, 0])
    for x in rows:
        if lcls(x["len"]) == cl:
            c[min(x["cost"], 4)][0] += x["taken"]
            c[min(x["cost"], 4)][1] += 1
    print(f"    length {cl}: " + " | ".join(f"cost {k}: {c[k][0]}/{c[k][1]}" for k in sorted(c)))
print("  by attacker length class x her length (2, 3, 4, 5+):")
for cl in ("2", "3", "4", "5-6", "7-9", "10-12"):
    c = defaultdict(lambda: [0, 0])
    for x in rows:
        if lcls(x["len"]) == cl:
            k = min(x["her"], 5)
            c[k][0] += x["taken"]
            c[k][1] += 1
    print(f"    length {cl}: " + " | ".join(f"her {k}{'+' if k == 5 else ''}: {c[k][0]}/{c[k][1]}" for k in sorted(c)))
print("  free chances only (cost 0) by attacker length x her length >= attacker length:")
c = defaultdict(lambda: [0, 0])
for x in rows:
    if x["cost"] == 0:
        k = (lcls(x["len"]), "her >= attacker" if x["her"] >= x["len"] else "her shorter")
        c[k][0] += x["taken"]
        c[k][1] += 1
print("    " + " | ".join(f"{k[0]}, {k[1]}: {v[0]}/{v[1]}" for k, v in sorted(c.items())))
if want_list:
    print("  not taken:")
    for x in sorted(rows, key=lambda x: (x["gid"], x["r"])):
        if not x["taken"]:
            print(f"    {x['gid']} {x['map']} r{x['r']} #{x['id']} L{x['len']} steps {x['steps']} cost {x['cost']} her L{x['her']} longest {x['longest']} own queen alive {x['oqa']}")
