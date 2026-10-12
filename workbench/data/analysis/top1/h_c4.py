#!/usr/bin/env python3
"""Candidate 4 ("do not give way"): two counts that the earlier files do not have.  Output: stdout -> h_out/c4.txt

1. Small intruders near the own queen (an enemy of 4 or shorter that comes within 4 path steps of the living queen;
   episodes of the lead's extract.py in q/<gid>.json): how often one of her team rams it.  For the live bot against
   the trade-on-contact build (tc30) on maps over 1,200 cells, the only maps where the two differ, and for the others.
   Question: is "nobody near our queen rams an intruder" the same thing as "we do not ram at contact"?
2. The tc30 trial on the common footing: wins on maps over 1,200 cells against what our own win rates per fine band
   (own / enemy total length at round 300, live bot) predict for the games it actually played.
"""
import csv
import json
import os
from collections import Counter, defaultdict

games = {r["game_id"]: r for r in csv.DictReader(open("games.csv"))}
TC = ("tc30-test-new", "tc30-dev1b-new")
TOP = {"306": "Vibing++", "91": "SSS", "264": "forgot"}

tab = defaultdict(Counter)
for gid, g in games.items():
    if g["map"] == "Schooltime" or not os.path.exists(f"q/{gid}.json"):
        continue
    d = json.load(open(f"q/{gid}.json"))
    big = int(g["cells"]) > 1200
    for s in "AB":
        o = "B" if s == "A" else "A"
        tid, oid = g[f"team{s}Id"], g[f"team{o}Id"]
        eo, es = float(g[f"team{o}Elo"] or 0), float(g[f"team{s}Elo"] or 0)
        grp = []
        if tid == "1119" and eo >= 2000:
            b = g["battle_id"]
            grp.append("meow tc30 build" if b in TC else "meow live" if (b.startswith("dl-") or b.endswith("-old")) else "meow other candidates")
        if oid == "1119" and es >= 2000:
            grp.append("opponents of meow")
        if tid in TOP and eo >= 2000:
            grp.append(TOP[tid])
        if not grp:
            continue
        for ep in d["sides"][s]["episodes"]:
            if ep["len"] > 4 or ep["min"] > 4:
                continue
            out = ep.get("outcome")
            if out == "it_rammed":
                out = "it rammed the queen" if ep.get("victim_queen") else "it rammed another of her dragons"
            for gname in grp:
                k = (gname, "over 1,200 cells" if big else "1,200 cells or fewer")
                tab[k]["intruders"] += 1
                tab[k][out] += 1
                if (ep.get("a6") or 0) >= 3:
                    tab[k]["intruders with 3+ own heads within 6 steps"] += 1
                    tab[k]["... rammed by a defender"] += out == "rammed_by_defender"
print("== 1. Small intruders within 4 steps of the own queen ==")
for k in sorted(tab):
    c = tab[k]
    n = c["intruders"]
    print(f"{k[0]:22s} {k[1]:22s} intruders {n:5d}: rammed by one of her team {c['rammed_by_defender']:4d} ({100 * c['rammed_by_defender'] / n:4.1f}%), "
          f"it rammed the queen {c['it rammed the queen']:4d} ({100 * c['it rammed the queen'] / n:4.1f}%), left {100 * c['left'] / n:.0f}%; "
          f"with 3+ own heads near: {c['... rammed by a defender']} of {c['intruders with 3+ own heads within 6 steps']}")

print("\n== 2. The tc30 trial against the band table ==")
base = json.load(open("h_out/base.json"))
FINE = [0, 0.2, 0.33, 0.5, 0.67, 0.85, 1.0, 1.25, 1.5, 2.0, 1e9]


def bi(x):
    for i in range(len(FINE) - 1):
        if FINE[i] <= x < FINE[i + 1]:
            return i


for scope, test in (("maps over 1,200 cells", lambda r: r["cells"] > 1200), ("maps of 1,200 cells or fewer", lambda r: r["cells"] <= 1200)):
    live = defaultdict(lambda: [0, 0])
    allm = defaultdict(lambda: [0, 0])
    for r in base:
        if "meow" not in r["groups"] or not test(r) or not r.get("my_tot300") or not r.get("op_tot300"):
            continue
        k = bi(r["my_tot300"] / r["op_tot300"])
        allm[k][0] += 1
        allm[k][1] += r["win"]
        if r["build"] == "live":
            live[k][0] += 1
            live[k][1] += r["win"]
    exp = 0.0
    n = w = 0
    early = [0, 0]
    for r in base:
        if "meow" not in r["groups"] or r["battle"] not in TC or not test(r):
            continue
        if not r.get("my_tot300") or not r.get("op_tot300"):
            early[0] += 1
            early[1] += r["win"]
            continue
        k = bi(r["my_tot300"] / r["op_tot300"])
        rate = live[k][1] / live[k][0] if live[k][0] >= 5 else (allm[k][1] / allm[k][0] if allm[k][0] else 0)
        exp += rate
        n += 1
        w += r["win"]
    print(f"{scope}: tc30 games reaching round 300: {n}, won {w}; expected from the live bot's win rate in the same fine band: {exp:.1f};"
          f" games that ended before round 300: {early[0]}, won {early[1]}")
