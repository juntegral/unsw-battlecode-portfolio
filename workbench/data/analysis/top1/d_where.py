#!/usr/bin/env python3
"""d_where.py [small|medium|large]: where on the board a short queen dies (sub-session A4, questions c and h).

For queens 4 or shorter, from q/*.json `per.q` (state at the start of every round): rounds spent and deaths in the
following 5 rounds, by
  home    wrapped manhattan distance from her start cell: 0-5, 6-10, 11-15, 16-25, 26+
  own6    own heads within 6 path steps: 0, 1-2, 3+
  open    cells within 4 path steps of her head (41 in open water): 20 or fewer (corridor / nook), 21-32, 33+
  exits   open sides of her cell (kelp only): 1-2, 3, 4
  enemy8  enemy heads within 8 path steps: 0, 1, 2+
A "death rate" is deaths per 1,000 rounds spent in that state (the death is charged to the state she was in 5
rounds before it, or at round 0 for earlier deaths, so that the last scramble does not decide the band).  Rams and
other deaths are shown apart.  Groups: meow live, meow, opp, forgot, SSS, Vibing++.  Opponents 2000+, no Schooltime.
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = {"306": "Vibing++", "91": "SSS", "264": "forgot"}
LIVE = {"dl-20261003", "dl-20261004", "stride-old", "passage2-test-old", "qh31-test-old", "tc30-dev1-old"}
GROUPS = ["meow live", "meow", "opp", "forgot", "SSS", "Vibing++"]
size_arg = sys.argv[1] if len(sys.argv) > 1 else None
LAG = 5


def size(c):
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


def bands(row):
    home = row[15]
    hb = "0-5" if home <= 5 else "6-10" if home <= 10 else "11-15" if home <= 15 else "16-25" if home <= 25 else "26+"
    a6 = row[6]
    ab = "0" if a6 == 0 else "1-2" if a6 <= 2 else "3+"
    ball = row[12]
    ob = "20 or fewer" if ball <= 20 else "21-32" if ball <= 32 else "33+"
    deg = row[13]
    db = "1-2" if deg <= 2 else str(deg)
    e8 = row[4]
    eb = "0" if e8 == 0 else "1" if e8 == 1 else "2+"
    return {"home": hb, "own6": ab, "open": ob, "exits": db, "enemy8": eb}


def main():
    t = defaultdict(lambda: defaultdict(Counter))
    for g in csv.DictReader(open(os.path.join(HERE, "games.csv"))):
        if g["map"] == "Schooltime":
            continue
        if size_arg and size(int(g["cells"])) != size_arg:
            continue
        q = None
        for s in "AB":
            o = "B" if s == "A" else "A"
            team, opp = g[f"team{s}Id"], g[f"team{o}Id"]
            elo_o, elo_s = float(g[f"team{o}Elo"] or 0), float(g[f"team{s}Elo"] or 0)
            groups = []
            if team in TOP and elo_o >= 2000:
                groups.append(TOP[team])
            if team == "1119" and elo_o >= 2000:
                groups.append("meow")
                if g["battle_id"] in LIVE:
                    groups.append("meow live")
            if opp == "1119" and elo_s >= 2000:
                groups.append("opp")
            if not groups:
                continue
            if q is None:
                q = json.load(open(os.path.join(HERE, "q", g["game_id"] + ".json")))
            sd = q["sides"][s]
            per = sd["per"]["q"]
            qd = sd["qdeath"]
            for r, row in enumerate(per):
                if not row or row[2] > 4:
                    continue
                b = bands(row)
                for grp in groups:
                    for dim, v in b.items():
                        t[grp][dim][(v, "rounds")] += 1
            if qd and qd["len"] <= 4:
                r0 = max(0, qd["round"] - LAG)
                row = per[r0] if r0 < len(per) and per[r0] else None
                if row and row[2] <= 4:
                    kind = "ram" if qd["reason"] == "headon" and qd["killer"] and qd["killer"]["team"] != s else "other"
                    b = bands(row)
                    for grp in groups:
                        for dim, v in b.items():
                            t[grp][dim][(v, kind)] += 1
    order = {"home": ["0-5", "6-10", "11-15", "16-25", "26+"], "own6": ["0", "1-2", "3+"], "open": ["20 or fewer", "21-32", "33+"],
             "exits": ["1-2", "3", "4"], "enemy8": ["0", "1", "2+"]}
    print(f"=== queens 4 or shorter{' on ' + size_arg + ' maps' if size_arg else ''}: share of rounds in each state | rammed per 1,000 rounds | dead another way per 1,000 rounds")
    for dim, vals in order.items():
        print(f"--- {dim}")
        print("group | " + " | ".join(vals))
        for grp in GROUPS:
            c = t[grp][dim]
            tot = sum(c[(v, "rounds")] for v in vals)
            if not tot:
                continue
            cells = []
            for v in vals:
                n = c[(v, "rounds")]
                cells.append(f"{100 * n / tot:.0f}% | {1000 * c[(v, 'ram')] / max(1, n):.1f} ({c[(v, 'ram')]}) | {1000 * c[(v, 'other')] / max(1, n):.1f} ({c[(v, 'other')]})")
            print(f"{grp} | " + " || ".join(cells))


if __name__ == "__main__":
    main()
