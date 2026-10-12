#!/usr/bin/env python3
"""b_opentab.py <game_id> ...: one line per game and team from the b_open.py outputs in b_out/ (sub-session A2).

Reads b_out/op2_<id>.txt (written by b_open.py <id> 100) and prints for both teams: units at rounds 30, 50, 100;
total length at round 100; natural pearls eaten in rounds 0-39, 40-89 and 0-99; splits in rounds 0-99; non-ram
deaths in rounds 0-99 (K+S+B+W) and head-on deaths; cells visited by round 100; mean distance from spawn at
round 60. Then the ratio of natural pearls eaten in rounds 40-89 between the two teams.
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GAMES = {g["game_id"]: g for g in csv.DictReader(open(os.path.join(HERE, "games.csv")))}
pat = re.compile(r"([AB]):\s*(\d+)u\s+(\d+)t \| ate\s*(\d+)/\s*(\d+) \| sp\s*(\d+) \| K\s*(\d+) S\s*(\d+) B\s*(\d+) W\s*(\d+) H\s*(\d+) \| paid\s*(\d+)/\s*(\d+) \| dist\s*([\d.]+) \| cov\s*(\d+)")
print("game | map | team | units r30 / r50 / r100 | total r100 | natural pearls r0-39 / r40-89 / r0-99 | splits r0-99 | non-ram deaths r0-99 | head-on deaths r0-99 | cells visited by r100 | mean dist from spawn r60")
for gid in sys.argv[1:]:
    g = GAMES[gid]
    rows = {}
    for line in open(os.path.join(HERE, "b_out", f"op2_{gid}.txt")):
        m = re.match(r"\s+r\s*(\d+) \|", line)
        if not m:
            continue
        r = int(m.group(1))
        for mm in pat.finditer(line):
            rows[(r, mm.group(1))] = [float(x) for x in mm.groups()[1:]]
    res = {}
    for s in "AB":
        def col(i, lo, hi):
            return int(sum(rows[(r, s)][i] for r in range(lo, hi, 10) if (r, s) in rows))
        u = {r: int(rows[(r, s)][0]) for r in (30, 50, 100) if (r, s) in rows}
        res[s] = dict(u=u, tot=int(rows[(100, s)][1]) if (100, s) in rows else 0, n039=col(2, 0, 40), n4089=col(2, 40, 90), n099=col(2, 0, 100),
                      sp=col(4, 0, 100), dead=col(5, 0, 100) + col(6, 0, 100) + col(7, 0, 100) + col(8, 0, 100), ho=col(9, 0, 100),
                      cov=int(rows[(100, s)][13]) if (100, s) in rows else 0, dist=rows[(60, s)][12] if (60, s) in rows else 0)
    for s in "AB":
        v = res[s]
        print(f"{gid} | {g['map']:15s} | {g['team%sName' % s][:12]:12s} | {v['u'].get(30, '-')} / {v['u'].get(50, '-')} / {v['u'].get(100, '-')} | {v['tot']} | {v['n039']} / {v['n4089']} / {v['n099']} | {v['sp']} | {v['dead']} | {v['ho']} | {v['cov']} | {v['dist']:.0f}")
    a, b_ = res["A"]["n4089"], res["B"]["n4089"]
    print(f"   natural pearls r40-89, {g['teamAName'][:12]} : {g['teamBName'][:12]} = {a} : {b_} ({a / max(1, b_):.2f})")
