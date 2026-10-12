#!/usr/bin/env python3
"""Candidate 3, part b: what the "leader" clock buys and what it costs, from h_out/base.json (q/ per-round series).

1. Units, total length and longest dragon at rounds 100-450 (means over games that reach the round), by map class
   (large = over 1,200 cells: our clock is round 150; other: round 300), for the live bot, the tc30 build, our
   opponents and the three top teams.
2. The same as changes over the window right after our clock (150 -> 300 on large maps, 300 -> 400 on the others).
3. Our large-map wins: all by the longest dragon?  Longest at round 300 / 400 in wins and losses.
Output: stdout -> h_out/c3b.txt
"""
import json
from collections import defaultdict

rows = json.load(open("h_out/base.json"))
CK = (100, 150, 200, 250, 300, 350, 400, 450)


def grp(r):
    g = []
    if "meow" in r["groups"]:
        g.append("meow live" if r["build"] == "live" else "meow cand")
        if r["battle"] in ("tc30-test-new", "tc30-dev1b-new"):
            g.append("meow tc30")
    if "opp_of_meow" in r["groups"]:
        g.append("opp of meow")
    for t in ("Vibing++", "SSS", "forgot"):
        if t in r["groups"]:
            g.append(t)
            g.append("top3")
    return g


def cls(r):
    return "large" if r["cells"] > 1200 else "other"


acc = defaultdict(lambda: [0, 0.0])
for r in rows:
    for g in grp(r):
        for rnd in CK:
            for f in ("uni", "tot", "lon"):
                v = r.get(f"my_{f}{rnd}")
                if v is None:
                    continue
                k = (g, cls(r), f, rnd)
                acc[k][0] += 1
                acc[k][1] += v
G = ["meow live", "meow cand", "meow tc30", "opp of meow", "Vibing++", "SSS", "forgot", "top3"]
for c in ("large", "other"):
    print(f"\n===== maps {'over 1,200 cells (our clock: round 150)' if c == 'large' else 'of 1,200 cells or fewer (our clock: round 300)'}")
    for f, name in (("uni", "units"), ("tot", "total length"), ("lon", "longest dragon")):
        print(f"-- {name} (mean; games that reach the round)   " + "  ".join(f"r{x}" for x in CK))
        for g in G:
            cells_ = []
            for rnd in CK:
                n, s = acc[(g, c, f, rnd)]
                cells_.append(f"{s / n:5.1f}" if n else "    -")
            n0 = acc[(g, c, f, CK[0])][0]
            print(f"   {g:12s} n={n0:4d}  " + " ".join(cells_))

print("\n===== 3. our games on maps over 1,200 cells: how they were won, and the longest dragon")
for g in ("meow live", "meow cand"):
    w = [r for r in rows if g in grp(r) and cls(r) == "large" and r["win"]]
    l = [r for r in rows if g in grp(r) and cls(r) == "large" and not r["win"]]
    def mean(xs, key):
        v = [r[key] for r in xs if r.get(key) is not None]
        return sum(v) / len(v) if v else float("nan")
    print(f"{g}: wins {len(w)} ({dict((k, sum(1 for r in w if r['end_type'] == k)) for k in set(r['end_type'] for r in w))}), losses {len(l)}")
    for name, xs in (("wins", w), ("losses", l)):
        print(f"   {name}: own longest r300 {mean(xs, 'my_lon300'):.1f}, r400 {mean(xs, 'my_lon400'):.1f}, final {sum(r['my_fin']['longest'] for r in xs) / max(1, len(xs)):.1f};"
              f" enemy longest r300 {mean(xs, 'op_lon300'):.1f}, r400 {mean(xs, 'op_lon400'):.1f}, final {sum(r['op_fin']['longest'] for r in xs) / max(1, len(xs)):.1f};"
              f" own total r300 {mean(xs, 'my_tot300'):.0f} vs {mean(xs, 'op_tot300'):.0f}; own units r300 {mean(xs, 'my_uni300'):.0f} vs {mean(xs, 'op_uni300'):.0f}")
