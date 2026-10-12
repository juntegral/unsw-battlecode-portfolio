#!/usr/bin/env python3
"""Lead's cross-check of A4's mirror claim with the lead's own turn-level chance data (q3v2, attacker's side):
in our games vs 2000+ (no Schooltime), in-view ram chances on OUR queen taken by the opponent, and on THEIR queen taken by us;
games with at least one chance; per 1,000 rounds the target queen lived. Split live bot / candidates."""
import csv
import json
from collections import defaultdict

t = defaultdict(lambda: defaultdict(float))
for g in csv.DictReader(open("games.csv")):
    if g["map"] == "Schooltime":
        continue
    for s in "AB":
        o = "B" if s == "A" else "A"
        if g[f"team{s}Id"] != "1119" or not g[f"team{o}Elo"] or float(g[f"team{o}Elo"]) < 2000:
            continue
        d3 = json.load(open(f"q3v2/{g['game_id']}.json"))
        q = json.load(open(f"q/{g['game_id']}.json"))
        build = "candidates" if g["battle_id"].endswith("-new") else "live"
        for grp in (build, "all"):
            for who, att, tgt in (("we on her", s, o), ("they on ours", o, s)):
                ch = [c for c in d3["chances"] if c[1] == att and c[9]]
                x = t[(grp, who)]
                x["games"] += 1
                x["chances"] += len(ch)
                x["taken"] += sum(c[5] for c in ch)
                x["games with chance"] += bool(ch)
                x["rounds with chance"] += len({c[0] for c in ch})
                x["rounds taken"] += len({c[0] for c in ch if c[5]})
                qd = q["sides"][tgt]["qdeath"]
                x["queen rounds"] += qd["round"] if qd else q["rounds"]
                small = [c for c in ch if c[3] <= 3]
                x["ch23"] += len(small)
                x["tk23"] += sum(c[5] for c in small)
for k in sorted(t):
    x = t[k]
    print(k, f"games {x['games']:.0f} | in-view chances {x['taken']:.0f}/{x['chances']:.0f} = {100 * x['taken'] / x['chances']:.0f}% | by 2-3-long {x['tk23']:.0f}/{x['ch23']:.0f} | "
          f"rounds with a chance {x['rounds with chance']:.0f} ({1000 * x['rounds with chance'] / x['queen rounds']:.1f} per 1,000 queen-rounds), rammed in {100 * x['rounds taken'] / x['rounds with chance']:.0f}% of them | games with a chance {x['games with chance']:.0f}")
