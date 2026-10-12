#!/usr/bin/env python3
"""Candidate 1, attack E: end states per team (round-500 games by queen state), recounted. Output: x_out/c1e.txt"""
from collections import Counter
import x_load as X
out = open("x_out/c1e.txt", "w")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.write(s + "\n")
gs = [g for g in X.games("c1") if g["d"] and X.is_csv(g)]
for name, pred in (("meow", lambda g, s: g[s] == X.ME), ("meow live", lambda g, s: g[s] == X.ME and X.build(g) == "live"),
                   ("Vibing++", lambda g, s: g[s] == X.VIB), ("SSS", lambda g, s: g[s] == X.SSS), ("forgot", lambda g, s: g[s] == X.FORGOT),
                   ("top three", lambda g, s: g[s] in X.TOP3)):
    c = Counter()
    for g in gs:
        for side in "AB":
            if not X.in_study(g, side) or not pred(g, side):
                continue
            d = g["d"]; es = X.other(side); e = d["end"]
            c["n"] += 1; c["won"] += X.won(g, side)
            if e["rounds"] < 500:
                k = "wipe"
            else:
                k = ("A" if e["qalive"][side] else "D") + ("A" if e["qalive"][es] else "D")
            c[k] += 1; c[k + " won"] += X.won(g, side)
            if k == "DD":
                qd = d["qdeath"][es]
                r = qd["reason"] == "headon" and qd.get("actor_team") == side
                c["DD rammed by us" if r else "DD other"] += 1
                c[("DD rammed by us" if r else "DD other") + " won"] += X.won(g, side)
    P("%-10s games %d won %d | wipe-out %d (won %d) | r500: own alive/her dead %d (won %d), both alive %d (won %d), both dead %d (won %d) [her queen rammed by this team %d (won %d), died another way %d (won %d)], own dead/her alive %d (won %d)" % (
        name, c["n"], c["won"], c["wipe"], c["wipe won"], c["AD"], c["AD won"], c["AA"], c["AA won"], c["DD"], c["DD won"],
        c["DD rammed by us"], c["DD rammed by us won"], c["DD other"], c["DD other won"], c["DA"], c["DA won"]))
