#!/usr/bin/env python3
"""The longest-dragon race: longest and total length at r200/300/400/end by team and size class, share of total held by
the longest, and the outcome of r500 games with both queens dead by total-length ratio at r400. Opp >= 2000, no Schooltime."""
import csv
import json
from collections import defaultdict
from statistics import median

TEAMS = {"306": "Vib", "91": "SSS", "264": "forgot", "1119": "meow"}


def size(c):
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


vals = defaultdict(list)
dd = defaultdict(lambda: [0, 0])
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
        if q["end_type"] == "wipe-out":
            continue
        me, he = q["sides"][s], q["sides"][o]
        name = TEAMS[g[f"team{s}Id"]]
        for sz in (size(int(g["cells"])), "all"):
            for r in (200, 300, 400, 499):
                if len(me["per"]["total"]) > r and me["per"]["total"][r]:
                    vals[(name, sz, r, "longest")].append(me["per"]["longest"][r])
                    vals[(name, sz, r, "total")].append(me["per"]["total"][r])
                    vals[(name, sz, r, "share")].append(me["per"]["longest"][r] / me["per"]["total"][r])
                    vals[(name, sz, r, "units")].append(me["per"]["units"][r])
            if me["final"]["queen"] == 0 and he["final"]["queen"] == 0 and len(me["per"]["total"]) > 400 and he["per"]["total"][400] and me["per"]["total"][400]:
                ratio = me["per"]["total"][400] / he["per"]["total"][400]
                cls = "<0.5" if ratio < 0.5 else "0.5-0.8" if ratio < 0.8 else "0.8-1.25" if ratio < 1.25 else "1.25-2" if ratio < 2 else "2+"
                dd[(name, sz, cls)][0] += 1
                dd[(name, sz, cls)][1] += g["winner"] == s
                # growth of the longest r400 -> end, at the same band
                vals[(name, sz, cls, "longest400")].append(me["per"]["longest"][400])
                vals[(name, sz, cls, "longestEnd")].append(me["final"]["longest"])
                vals[(name, sz, cls, "her400")].append(he["per"]["longest"][400])
                vals[(name, sz, cls, "herEnd")].append(he["final"]["longest"])
for sz in ("all", "large", "medium", "small"):
    print(f"\n===== {sz}: medians in r500 games (round: longest / total / units / longest share of total)")
    for name in ("meow", "Vib", "SSS", "forgot"):
        print(f"  {name:6s} " + " | ".join(
            f"r{r}: {median(vals[(name, sz, r, 'longest')]):.0f} / {median(vals[(name, sz, r, 'total')]):.0f} / {median(vals[(name, sz, r, 'units')]):.0f} / {100 * median(vals[(name, sz, r, 'share')]):.0f}%"
            for r in (200, 300, 400, 499) if vals[(name, sz, r, 'longest')]))
    print("  r500 games with both queens dead at the end, by own/enemy total length at r400: wins/games; median own longest r400 -> end vs enemy's")
    for cls in ("<0.5", "0.5-0.8", "0.8-1.25", "1.25-2", "2+"):
        for name in ("meow", "Vib", "SSS", "forgot"):
            n, w = dd[(name, sz, cls)]
            if n:
                print(f"    {cls:8s} {name:6s} {w:3d}/{n:3d} ({100 * w / n:3.0f}%) own longest {median(vals[(name, sz, cls, 'longest400')]):.0f} -> {median(vals[(name, sz, cls, 'longestEnd')]):.0f}, "
                      f"enemy {median(vals[(name, sz, cls, 'her400')]):.0f} -> {median(vals[(name, sz, cls, 'herEnd')]):.0f}")
