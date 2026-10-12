#!/usr/bin/env python3
"""How our games end by map size class (600 or fewer / 601-1,200 / over 1,200 cells). Output: x_out/small.txt"""
from collections import Counter
import x_load as X
out = open("x_out/small.txt", "w")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.write(s + "\n")
gs = [g for g in X.games("c1") if g["d"] and X.is_csv(g)]
for lab, f in (("600 cells or fewer", lambda c: c <= 600), ("601 to 1,200", lambda c: 600 < c <= 1200), ("over 1,200", lambda c: c > 1200)):
    c = Counter()
    for g in gs:
        side = X.side_of(g, X.ME)
        if side is None or not X.in_study(g, side) or not f(g["cells"]):
            continue
        d = g["d"]; e = d["end"]; es = X.other(side)
        c["n"] += 1; c["w"] += X.won(g, side)
        if e["rounds"] < 500:
            k = "wipe-out before round 300" if e["rounds"] <= 300 else "wipe-out later"
        else:
            k = "round 500"
        c[k] += 1; c[k + " won"] += X.won(g, side)
        c["our queen alive at the end"] += e["qalive"][side]
    P("%-20s games %d won %d | wipe-out before round 300: %d (won %d) | wipe-out later: %d (won %d) | round 500: %d (won %d) | our queen alive at the end %d" % (
        lab, c["n"], c["w"], c["wipe-out before round 300"], c["wipe-out before round 300 won"], c["wipe-out later"], c["wipe-out later won"],
        c["round 500"], c["round 500 won"], c["our queen alive at the end"]))
