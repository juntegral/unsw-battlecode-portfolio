#!/usr/bin/env python3
"""d_cut.py [list]: how each team's queen splits, and what happens after she cuts herself short (sub-session A4).

From q/*.json (qsplits = [round, length before, parent keeps, child gets]).  Opponents rated 2000+, no Schooltime.
  mother  : length 4-5, she keeps 2-3 (the ordinary growth split)
  shed    : she keeps 3 or more and the child gets 2-3 (tail shed; with no free cell this is a way to wait)
  cut     : length 6 or more and she keeps 2-3 (everything else goes to the child)
  other   : the rest
For cuts: the length thrown away, whether she is dead within 5 / 20 rounds, and the result of the game.
"""
import csv
import json
import sys
from collections import Counter, defaultdict

T = {"1119": "meow", "306": "Vibing++", "91": "SSS", "264": "forgot"}
LIVE = {"dl-20261003", "dl-20261004", "stride-old", "passage2-test-old", "qh31-test-old", "tc30-dev1-old"}
want = len(sys.argv) > 1 and sys.argv[1] == "list"
tab = defaultdict(Counter)
cuts = defaultdict(list)
for g in csv.DictReader(open("games.csv")):
    if g["map"] == "Schooltime":
        continue
    q = None
    for s in "AB":
        o = "B" if s == "A" else "A"
        groups = []
        if g[f"team{s}Id"] in T and g[f"team{o}Elo"] and float(g[f"team{o}Elo"]) >= 2000:
            groups.append(T[g[f"team{s}Id"]])
            if g[f"team{s}Id"] == "1119":
                groups.append("meow live" if g["battle_id"] in LIVE else "meow candidates")
        if g[f"team{o}Id"] == "1119" and g[f"team{s}Elo"] and float(g[f"team{s}Elo"]) >= 2000:
            groups.append("opp")
        if not groups:
            continue
        if q is None:
            q = json.load(open(f"q/{g['game_id']}.json"))
        sd = q["sides"][s]
        qd = sd["qdeath"]
        per = sd["per"]["q"]
        had = False
        for r, before, plen, clen in sd["qsplits"]:
            kind = ("mother" if before <= 5 else "cut" if plen <= 3 else "shed" if clen <= 3 else "other")
            free = per[r][11] if r < len(per) and per[r] else None
            for grp in groups:
                c = tab[grp]
                c[kind] += 1
                c[f"{kind} with no free cell"] += free == 0
                if kind == "cut":
                    c["segments given away by cuts"] += clen
                    dead5 = bool(qd) and qd["round"] - r <= 5
                    dead20 = bool(qd) and qd["round"] - r <= 20
                    c["cut: dead within 5 rounds"] += dead5
                    c["cut: dead within 20 rounds"] += dead20
                    c["cut: 10+ long before"] += before >= 10
                    if not had:
                        c["games with a cut"] += 1
                    cuts[grp].append((g["game_id"], g["map"], g["battle_id"], r, before, plen, clen, free,
                                      qd["round"] if qd else None, qd["reason"] if qd else "alive",
                                      "W" if g["winner"] == s else "L", g["end_type"], int(g[f"final_queen_length_{o}"] or 0)))
            if kind == "cut":
                had = True
        for grp in groups:
            tab[grp]["games"] += 1
cols = ["meow", "meow live", "meow candidates", "opp", "forgot", "SSS", "Vibing++"]
keys = ["games", "mother", "mother with no free cell", "shed", "shed with no free cell", "cut", "cut with no free cell", "games with a cut",
        "cut: 10+ long before", "segments given away by cuts", "cut: dead within 5 rounds", "cut: dead within 20 rounds", "other"]
print("measure | " + " | ".join(cols))
for k in keys:
    print(f"{k} | " + " | ".join(str(tab[c][k]) for c in cols))
if want:
    for grp in ("meow", "opp"):
        print(f"\ncuts of {grp}: game, map, run, round, before -> keeps + child, free cells then, queen death (round, reason), result, end type, enemy queen final length")
        for row in sorted(cuts[grp], key=lambda x: (x[1], x[3])):
            print("  ", *row)
