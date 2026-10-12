#!/usr/bin/env python3
"""b_mychances.py <game_id> ...: q3v2 ram chances on the enemy queen in the games read, per team (sub-session A2).

Per game and team: chances in view (taken / all) and not in view (taken / all), and every in-view chance that was
not taken and every not-in-view chance of at most 6 steps (round, id, length, steps, paid steps, her length).
Totals per team id at the end.
"""
import csv
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
GAMES = {g["game_id"]: g for g in csv.DictReader(open(os.path.join(HERE, "games.csv")))}
tot = defaultdict(lambda: [0, 0, 0, 0])
for gid in sys.argv[1:]:
    g = GAMES[gid]
    ch = json.load(open(os.path.join(HERE, "q3v2", gid + ".json")))["chances"]
    for s in "AB":
        t = g["team%sId" % s]
        mine = [c for c in ch if c[1] == s]
        iv = [c for c in mine if c[9]]
        nv = [c for c in mine if not c[9]]
        tot[t][0] += sum(c[5] for c in iv)
        tot[t][1] += len(iv)
        tot[t][2] += sum(c[5] for c in nv)
        tot[t][3] += len(nv)
        if not mine:
            continue
        print(f"{gid} {g['map']} {g['team%sName' % s][:14]}: in view {sum(c[5] for c in iv)}/{len(iv)} taken; not in view {sum(c[5] for c in nv)}/{len(nv)} taken")
        for c in iv:
            if not c[5]:
                free = -(-c[3] // 4)
                print(f"     in view, NOT taken: r{c[0]} #{c[2]} L{c[3]} steps {c[4]} paid {max(0, c[4] - free)} her L{c[6]} own queen alive {c[8]} longest {c[7]}")
        short = [c for c in nv if c[4] <= 6]
        if short:
            print("     not in view, 6 steps or fewer: " + "; ".join(f"r{c[0]} #{c[2]} L{c[3]} steps {c[4]} her L{c[6]}{' TAKEN' if c[5] else ''}" for c in short))
print()
for t, v in tot.items():
    print(f"team {t}: in view {v[0]}/{v[1]} taken; not in view {v[2]}/{v[3]} taken")
