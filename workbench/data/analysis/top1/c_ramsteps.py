#!/usr/bin/env python3
"""c_ramsteps.py [size=large]: from how far away is a ram made, and by dragons of which length? (q/<id>.json, no replay walking)

A q head-on record is [round, rammer side, rammer id, rammer length, steps used, steps required, victim side, victim id,
victim length, ...]. "Steps used" is the number of steps of the rammer's move that ended in the enemy head: 1 = the two
heads were on neighbouring cells when the turn began; 2 or more = the rammer came from further away in one turn.
Only rams between the two teams are counted.

Groups: meow (runs without TRADE_CONTACT), meow (TRADE_CONTACT runs tc30-test-new and tc30-dev1b-new), the opponents in
those two groups of games, test4 and WeHaveQuizzes against the top three, forgot, SSS, Vibing++ (opponents rated 2000+).
Per group and phase (rounds 0-149, 150-299, 300+): rams made per game; share made with 1 / 2 / 3+ steps; mean length
of the rammer and of the victim; share of victims of length 5 or more; share of rammers of length 5 or more.
"""
import csv
import json
import sys
from collections import Counter, defaultdict

want = sys.argv[1] if len(sys.argv) > 1 else "large"
TOP = {306: "Vibing++", 91: "SSS", 264: "forgot"}
TC = ("tc30-test-new", "tc30-dev1b-new")
PH = ["r0-149", "r150-299", "r300+"]
acc = defaultdict(Counter)
games = Counter()
for g in csv.DictReader(open("games.csv")):
    if g["map"] == "Schooltime":
        continue
    size = "small" if g["map_size"].startswith("small") else "medium" if g["map_size"].startswith("medium") else "large"
    if want not in (size, g["map"]):
        continue
    ids = {s: int(g[f"team{s}Id"]) for s in "AB"}
    grp = {}
    for s in "AB":
        o = "B" if s == "A" else "A"
        try:
            oelo = float(g[f"team{o}Elo"])
        except ValueError:
            oelo = 0
        t, ot = ids[s], ids[o]
        if t == 1119 and oelo >= 2000:
            tc = g["battle_id"] in TC
            grp[s] = "meow, TRADE_CONTACT runs" if tc else "meow, other runs"
            grp[o] = "opponents of meow, TRADE_CONTACT runs" if tc else "opponents of meow, other runs"
        elif t in TOP and oelo >= 2000:
            grp[s] = TOP[t]
            if ot in (19, 87):
                grp[o] = "test4 and WHQ against the top three"
    if not grp:
        continue
    q = json.load(open(f"q/{g['game_id']}.json"))
    for s, name in grp.items():
        games[name] += 1
    for h in q["headons"]:
        r, rs, rid, rlen, used, req, vs, vid, vlen = h[:9]
        if rs == vs or rs not in grp:
            continue
        ph = PH[0] if r < 150 else PH[1] if r < 300 else PH[2]
        for key in (ph, "all"):
            a = acc[(grp[rs], key)]
            a["n"] += 1
            a["s1" if used <= 1 else "s2" if used == 2 else "s3"] += 1
            a["rlen"] += rlen
            a["vlen"] += vlen
            a["v5"] += vlen >= 5
            a["r5"] += rlen >= 5
            a["r2"] += rlen <= 2
print(f"=== RAM STEPS, {want} maps: rams made by each group (between the two teams only)")
print("group (games) | phase | rams made per game | made with 1 step % / 2 steps % / 3 or more % | mean length rammer / victim | rammer 2 long % | rammer 5+ % | victim 5+ %")
order = ["meow, other runs", "meow, TRADE_CONTACT runs", "opponents of meow, other runs", "opponents of meow, TRADE_CONTACT runs",
         "test4 and WHQ against the top three", "forgot", "SSS", "Vibing++"]
for name in order:
    n = games[name]
    if not n:
        continue
    for ph in PH + ["all"]:
        a = acc[(name, ph)]
        m = max(1, a["n"])
        print(f"{name:38s} ({n:3d}) | {ph:8s} | {a['n'] / n:5.1f} | {100 * a['s1'] / m:3.0f}% / {100 * a['s2'] / m:3.0f}% / {100 * a['s3'] / m:3.0f}% | "
              f"{a['rlen'] / m:4.1f} / {a['vlen'] / m:4.1f} | {100 * a['r2'] / m:3.0f}% | {100 * a['r5'] / m:3.0f}% | {100 * a['v5'] / m:3.0f}%")
    print()
