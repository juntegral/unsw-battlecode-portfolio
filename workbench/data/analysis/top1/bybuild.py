#!/usr/bin/env python3
"""Our games split by run (battle id = which build played): in-view ram chances on the enemy queen and how many were
taken, rams on her per game, her survival, our queen's fate, wins. Opp elo >= 2000, Schooltime excluded.
Uses games.csv (battle_id), q/*.json, q3v2/*.json.
"""
import csv
import json
from collections import defaultdict

rows = defaultdict(lambda: defaultdict(float))
order = {}
for g in csv.DictReader(open("games.csv")):
    if g["map"] == "Schooltime":
        continue
    for s in "AB":
        if g[f"team{s}Id"] != "1119":
            continue
        o = "B" if s == "A" else "A"
        if not g[f"team{o}Elo"] or float(g[f"team{o}Elo"]) < 2000:
            continue
        bid = g["battle_id"]
        if bid.startswith("dl-"):
            bid = "ladder " + bid[3:] + (" (also smoke copy)" if "smoke" in g["sources"] else "")
        order.setdefault(bid, g["completed_at"])
        d = json.load(open(f"q/{g['game_id']}.json"))
        d3 = json.load(open(f"q3v2/{g['game_id']}.json"))
        r = rows[bid]
        big = int(g["cells"]) > 1200
        r["games"] += 1
        r["wins"] += g["winner"] == s
        ch = [c for c in d3["chances"] if c[1] == s and c[9]]
        r["chances"] += len(ch)
        r["taken"] += sum(c[5] for c in ch)
        r["ch23"] += sum(1 for c in ch if c[3] <= 3)
        r["tk23"] += sum(c[5] for c in ch if c[3] <= 3)
        r["ch4p"] += sum(1 for c in ch if c[3] >= 4)
        r["tk4p"] += sum(c[5] for c in ch if c[3] >= 4)
        qd = d["sides"][o]["qdeath"]
        killed = bool(qd and qd["reason"] == "headon" and qd["killer"] and qd["killer"]["team"] == s)
        r["kills"] += killed
        r["her alive end"] += d["sides"][o]["final"]["queen"] > 0
        r["our alive end"] += d["sides"][s]["final"]["queen"] > 0
        mq = d["sides"][s]["qdeath"]
        r["our q rammed"] += bool(mq and mq["reason"] == "headon" and mq["killer"] and mq["killer"]["team"] == o)
        r["our q self"] += bool(mq and not (mq["reason"] == "headon" and mq["killer"] and mq["killer"]["team"] == o))
        r["missed game"] += bool(ch) and not killed
        if big:
            r["big games"] += 1
            r["big kills"] += killed
            r["big chances"] += len(ch)
            r["big taken"] += sum(c[5] for c in ch)
print("run | games | wins | in-view chances taken (all) | by 2-3-long | by 4+ | rams on her queen per game | her queen alive at end | our queen: alive / rammed / own move | games with a chance and no kill | big maps: games, kills, chances taken")
for bid in sorted(rows, key=lambda b: order[b]):
    r = rows[bid]
    n = r["games"]
    print(f"{bid:34s} | {n:3.0f} | {r['wins']:3.0f} | {r['taken']:3.0f}/{r['chances']:3.0f} | {r['tk23']:3.0f}/{r['ch23']:3.0f} | {r['tk4p']:2.0f}/{r['ch4p']:3.0f} | "
          f"{r['kills'] / n:.2f} | {r['her alive end'] / n:.2f} | {r['our alive end'] / n:.2f} / {r['our q rammed'] / n:.2f} / {r['our q self'] / n:.2f} | {r['missed game']:2.0f} | "
          f"{r['big games']:2.0f}, {r['big kills']:2.0f}, {r['big taken']:2.0f}/{r['big chances']:3.0f}")
