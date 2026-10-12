#!/usr/bin/env python3
"""How games are won from behind: by total length at round 300 (behind / ahead), result and end type, queen states at the end.
Opp elo >= 2000, Schooltime excluded. Groups: top three, meow (all builds)."""
import csv
import json
from collections import defaultdict

TEAMS = {"306": "Vibing++", "91": "SSS", "264": "forgot", "1119": "meow"}


def size(c):
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


tab = defaultdict(lambda: defaultdict(int))
for g in csv.DictReader(open("games.csv")):
    if g["map"] == "Schooltime":
        continue
    q = None
    for s in "AB":
        o = "B" if s == "A" else "A"
        if g[f"team{s}Id"] not in TEAMS or not g[f"team{o}Elo"] or float(g[f"team{o}Elo"]) < 2000:
            continue
        if q is None:
            q = json.load(open(f"q/{g['game_id']}.json"))
        me, he = q["sides"][s], q["sides"][o]
        mine, theirs = me["per"]["total"], he["per"]["total"]
        if not (len(mine) > 300 and len(theirs) > 300 and mine[300] and theirs[300]):
            continue
        ratio = mine[300] / theirs[300]
        cls = "behind <0.67" if ratio < 0.67 else "behind 0.67-1" if ratio < 1 else "ahead 1-1.5" if ratio < 1.5 else "ahead 1.5+"
        won = g["winner"] == s
        mq300 = bool(me["per"]["q"][300])
        hq300 = bool(he["per"]["q"][300])
        mqe, hqe = me["final"]["queen"] > 0, he["final"]["queen"] > 0
        for grp in (TEAMS[g[f"team{s}Id"]], "top three" if g[f"team{s}Id"] != "1119" else None):
            if grp is None:
                continue
            for sz in (size(int(g["cells"])), "all sizes"):
                t = tab[(grp, sz, cls)]
                t["n"] += 1
                t["won"] += won
                if won:
                    t["won by " + g["end_type"]] += 1
                    t["won, her queen died after r300"] += hq300 and not hqe
                    t["won, own queen alive at end"] += mqe
                    t["won, longest at r300 was ours"] += me["per"]["longest"][300] > he["per"]["longest"][300]
                else:
                    t["lost by " + g["end_type"]] += 1
                    t["lost, own queen died after r300"] += mq300 and not mqe
                t["own queen alive r300"] += mq300
                t["her queen alive r300"] += hq300
                t["own longest > hers at r300"] += me["per"]["longest"][300] > he["per"]["longest"][300]
for sz in ("all sizes", "large", "medium", "small"):
    print(f"\n===== {sz} =====")
    for cls in ("behind <0.67", "behind 0.67-1", "ahead 1-1.5", "ahead 1.5+"):
        print(f"--- total length at r300 own/enemy: {cls}")
        for grp in ("top three", "Vibing++", "SSS", "forgot", "meow"):
            t = tab[(grp, sz, cls)]
            if not t["n"]:
                continue
            keys = [k for k in sorted(t) if k not in ("n", "won")]
            print(f"  {grp:10s} n={t['n']:4d} won {t['won']:3d} ({100 * t['won'] / t['n']:.0f}%) | " + ", ".join(f"{k} {t[k]}" for k in keys))
