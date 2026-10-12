#!/usr/bin/env python3
"""d_t4.py: the queens of test4 (19) and WeHaveQuizzes (87) by kind of end, against meow and against the top three
(sub-session A4, question f: what happens to a circling queen when real hunters find her).

Uses d_out/cls (both sides of every walked game are stored) and d_tab.classify().  Also prints, for test4's rammed
queens, how many rounds before the ram she had last been on a loop (4 or fewer cells in 12 rounds), from d_out/life.
"""
import csv
import glob
import json
import os
from collections import Counter, defaultdict

import d_tab

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = {"306", "91", "264"}
games = {g["game_id"]: g for g in csv.DictReader(open(os.path.join(HERE, "games.csv")))}
tab = defaultdict(Counter)
rounds = Counter()
lastloop = defaultdict(list)
for f in sorted(glob.glob(os.path.join(HERE, "d_out", "cls", "*.json"))):
    d = json.load(open(f))
    g = games[str(d["game_id"])]
    for s in "AB":
        o = "B" if s == "A" else "A"
        team, opp = g[f"team{s}Id"], g[f"team{o}Id"]
        if team not in ("19", "87"):
            continue
        who = "test4" if team == "19" else "WHQ"
        vs = "meow" if opp == "1119" else "the top three" if opp in TOP else None
        if vs is None:
            continue
        key = f"{who} against {vs}"
        sd = d["sides"][s]
        kind, det = d_tab.classify(sd)
        tab[key][kind] += 1
        tab[key]["n"] += 1
        rounds[key] += det["r"] if kind != "alive" else int(g["rounds"])
        if kind.startswith("ram"):
            lp = os.path.join(HERE, "d_out", "life", g["game_id"] + ".json")
            if os.path.exists(lp):
                pos = json.load(open(lp))["sides"][s]["pos"]
                r = det["r"]
                back = None
                for rr in range(min(r, len(pos) - 1), 10, -1):
                    seg = pos[rr - 11:rr + 1]
                    if all(seg) and len({tuple(c) for c in seg}) <= 4:
                        back = r - rr
                        break
                lastloop[key].append((back, g["game_id"], g["map"], r, kind, det["k"]["len"], det["k"]["steps"]))
keys = sorted(tab)
print("kind | " + " | ".join(keys))
for k in d_tab.ORDER:
    if any(tab[x][k] for x in keys):
        print(f"{k} | " + " | ".join(f"{tab[x][k]} ({100 * tab[x][k] / tab[x]['n']:.0f}%)" for x in keys))
print("games | " + " | ".join(str(tab[x]["n"]) for x in keys))
print("deaths per 1,000 queen-rounds | " + " | ".join(f"{1000 * (tab[x]['n'] - tab[x]['alive']) / rounds[x]:.2f}" for x in keys))
print("rams per 1,000 queen-rounds | " + " | ".join(f"{1000 * sum(v for k, v in tab[x].items() if k.startswith('ram')) / rounds[x]:.2f}" for x in keys))
for key in keys:
    xs = lastloop[key]
    c = Counter("on a loop in her last 3 rounds" if b is not None and b <= 3 else "4-20 rounds before" if b is not None and b <= 20 else "longer ago" if b is not None else "never on a loop" for b, *_ in xs)
    print(f"\n{key}: rammed queens {len(xs)}; when she was last on a loop: {dict(c)}")
    for row in sorted(xs, key=lambda t: (t[0] is None, t[0]))[:12]:
        print("   ", row)
