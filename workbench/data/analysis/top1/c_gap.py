#!/usr/bin/env python3
"""c_gap.py [team=1119] [--games]: when does the unit gap open? From q/<id>.json (units and total length per round).

For every game of the team against a 2000+ opponent (Schooltime left out): the unit ratio own / enemy at rounds 50,
100, 150, 200, 250, 300; the first round from which the ratio stays below 0.8 until the end of the game ("for good");
the same for total length; the round of the first ram of the game. Then tables by map and by opponent:
how many games fall behind for good in rounds 0-49, 50-99, 100-149, 150-199, 200-299, 300+, never.
"""
import csv
import json
import sys
from collections import Counter, defaultdict

team = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 1119
show = "--games" in sys.argv
GAMES = list(csv.DictReader(open("games.csv")))


def for_good(a, b, thr=0.8):
    """First round r such that a[t] / b[t] < thr for every t >= r (None if the last round is not below)."""
    n = min(len(a), len(b))
    if n == 0:
        return None
    last = None
    for t in range(n - 1, -1, -1):
        if b[t] > 0 and a[t] / b[t] < thr:
            last = t
        else:
            break
    return last


def bucket(r):
    if r is None:
        return "never"
    return "0-49" if r < 50 else "50-99" if r < 100 else "100-149" if r < 150 else "150-199" if r < 200 else "200-299" if r < 300 else "300+"


ORDER = ("0-49", "50-99", "100-149", "150-199", "200-299", "300+", "never")
bymap = defaultdict(Counter)
byopp = defaultdict(Counter)
bysize = defaultdict(Counter)
ratio = defaultdict(lambda: defaultdict(list))
tratio = defaultdict(lambda: defaultdict(list))
cnt3 = defaultdict(Counter)
rows = []
for g in GAMES:
    if g["map"] == "Schooltime":
        continue
    for s in "AB":
        if int(g[f"team{s}Id"]) != team:
            continue
        o = "B" if s == "A" else "A"
        try:
            if float(g[f"team{o}Elo"]) < 2000:
                continue
        except ValueError:
            continue
        q = json.load(open(f"q/{g['game_id']}.json"))
        ua, ub = q["sides"][s]["per"]["units"], q["sides"][o]["per"]["units"]
        ta, tb = q["sides"][s]["per"]["total"], q["sides"][o]["per"]["total"]
        fu = for_good(ua, ub)
        ft = for_good(ta, tb)
        cross = [h for h in q["headons"] if h[1] != h[6]]   # head-ons inside one team are not rams
        first_ram = cross[0][0] if cross else None
        size = g["map_size"].split("<")[0].split(">")[0].rstrip("0123456789-")
        won = g["winner"] == s
        opp = g[f"team{o}Name"][:14]
        bymap[(size, g["map"])][bucket(fu)] += 1
        bymap[(size, g["map"])]["n"] += 1
        bymap[(size, g["map"])]["won"] += won
        byopp[(size, opp)][bucket(fu)] += 1
        byopp[(size, opp)]["n"] += 1
        byopp[(size, opp)]["won"] += won
        bysize[size][bucket(fu)] += 1
        bysize[size]["n"] += 1
        bysize[size + " total"][bucket(ft)] += 1
        bysize[size + " total"]["n"] += 1
        rr = []
        for r in (50, 100, 150, 200, 250, 300):
            if r < len(ua) and r < len(ub) and ub[r] > 0:
                x = ua[r] / ub[r]
                rr.append(f"{x:4.2f}")
                ratio[(size, opp)][r].append(x)
                ratio[(size, "all")][r].append(x)
                ratio[(size, g["map"])][r].append(x)
            else:
                rr.append("  - ")
            if r < len(ta) and r < len(tb) and tb[r] > 0:
                y = ta[r] / tb[r]
                for key in ((size, opp), (size, "all"), (size, g["map"]), (size, g["map"], opp)):
                    tratio[key][r].append(y)
                    if key[-1] == opp and len(key) == 3:
                        ratio[key][r].append(ua[r] / ub[r] if ub[r] else 0)
        cnt3[(size, g["map"], opp)]["n"] += 1
        cnt3[(size, g["map"], opp)]["won"] += won
        cnt3[(size, g["map"], opp)][bucket(fu)] += 1
        rows.append((size, g["map"], g["game_id"], opp, "W" if won else "L", rr, fu, ft, first_ram,
                     [f"{ua[r]}:{ub[r]}" if r < len(ua) and r < len(ub) else "-" for r in (50, 100, 150, 200, 300)],
                     [f"{ta[r]}:{tb[r]}" if r < len(ta) and r < len(tb) else "-" for r in (50, 100, 150, 200, 300)]))


def med(v):
    return f"{sorted(v)[len(v) // 2]:4.2f}" if v else "  - "

print(f"=== GAP team {team}: first round from which own units / enemy units stays below 0.8 until the end of the game (opponents 2000+, Schooltime left out)")
print("  by map size (units), then the same for total length:")
for k in sorted(bysize):
    c = bysize[k]
    print(f"    {k:14s} n {c['n']:3d} | " + " | ".join(f"{b} {c[b]:3d}" for b in ORDER))
print("  by map:")
for k in sorted(bymap):
    c = bymap[k]
    rr = ratio[(k[0], k[1])]
    print(f"    {k[0]:7s} {k[1]:18s} n {c['n']:3d} won {c['won']:3d} | " + " | ".join(f"{b} {c[b]:3d}" for b in ORDER) +
          " | median unit ratio r50/100/150/200/300: " + " ".join(med(rr[r]) for r in (50, 100, 150, 200, 300)) +
          " | median total-length ratio: " + " ".join(med(tratio[k][r]) for r in (50, 100, 150, 200, 300)))
print("  by map and opponent (4 or more games): n, won, behind for good in units by bucket, median unit ratio, median total-length ratio at r50/100/150/200/300")
for k in sorted(cnt3):
    c = cnt3[k]
    if c["n"] < 4:
        continue
    print(f"    {k[0]:7s} {k[1]:16s} {k[2]:14s} n {c['n']:3d} won {c['won']:3d} | " + " | ".join(f"{b} {c[b]:2d}" for b in ORDER) +
          " | units " + " ".join(med(ratio[k][r]) for r in (50, 100, 150, 200, 300)) +
          " | total " + " ".join(med(tratio[k][r]) for r in (50, 100, 150, 200, 300)))
print("  by opponent (4 or more games):")
for k in sorted(byopp):
    c = byopp[k]
    if c["n"] < 4:
        continue
    rr = ratio[k]
    print(f"    {k[0]:7s} {k[1]:14s} n {c['n']:3d} won {c['won']:3d} | " + " | ".join(f"{b} {c[b]:3d}" for b in ORDER) +
          " | median unit ratio r50/100/150/200/300: " + " ".join(med(rr[r]) for r in (50, 100, 150, 200, 300)) +
          " | median total-length ratio: " + " ".join(med(tratio[k][r]) for r in (50, 100, 150, 200, 300)))
if show:
    print("  games: size map id opponent result | unit ratio r50 r100 r150 r200 r250 r300 | behind for good from (units, total) | first ram | units own:enemy at r50 r100 r150 r200 r300 | total length own:enemy at the same rounds")
    for size, m, gid, opp, res, rr, fu, ft, fr, uu, tt in sorted(rows):
        print(f"    {size:6s} {m:16s} {gid} {opp:14s} {res} | {' '.join(rr)} | {str(fu):>4s} {str(ft):>4s} | ram {str(fr):>4s} | {' '.join(uu)} | {' '.join(tt)}")
