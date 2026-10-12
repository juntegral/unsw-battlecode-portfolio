#!/usr/bin/env python3
"""Candidate 2: our queen's cuts (boxed in, 6 or longer, keeps 2-3) one by one: map, round, length, what followed.
And the top three's boxed-in splits by map. Own code on x_out/c2/ and x_out/c1/. Output: x_out/c2cut.txt"""
from collections import Counter, defaultdict
import x_load as X
out = open("x_out/c2cut.txt", "w")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.write(s + "\n")
gs = [g for g in X.games("c2") if g["d"] and X.is_csv(g)]
g1 = {g["gid"]: g for g in X.games("c1") if g["d"]}
bymap = Counter(); early = Counter()
rows = []
for g in gs:
    side = X.side_of(g, X.ME)
    if side is None or not X.in_study(g, side):
        continue
    d = g["d"]; qd = d["qdeath"].get(side); es = X.other(side)
    e = g1[g["gid"]]["d"]["end"]
    for s in d["splits"]:
        if s["side"] == side and s["n_legal"] == 0 and s["L"] >= 6 and s["keep"] <= 3 and s["child"] > 2:
            bymap[g["map"]] += 1
            early[g["map"], "round 0-5" if s["r"] <= 5 else "later"] += 1
            dr = qd["r"] if qd else None
            rows.append((s["r"], g["gid"], g["map"], s["L"], s["keep"], (dr - s["r"]) if dr is not None else None, qd["reason"] if qd else "alive",
                         "WON" if X.won(g, side) else "lost", e["rounds"], e["qalive"][es], e["st"][es][4]))
P("our cuts of a boxed-in queen of 6 or more:", len(rows), "by map:", dict(bymap), dict(early))
P("the ones after round 5, one by one:")
for r in sorted(rows):
    if r[0] > 5:
        P("   round %-3d game %d %-15s queen %2d long keeps %d; she died %s rounds later (%s); game %s (rounds %d); enemy queen alive at the end: %s (length %d)" % r)
ea = [r for r in rows if r[0] <= 5]
P("the %d cuts in rounds 0-5: she died within 5 rounds in %d, within 20 in %d, later in %d, alive at the end in %d; games won %d" % (
    len(ea), sum(1 for r in ea if r[5] is not None and r[5] <= 5), sum(1 for r in ea if r[5] is not None and r[5] <= 20),
    sum(1 for r in ea if r[5] is not None and r[5] > 20), sum(1 for r in ea if r[5] is None), sum(1 for r in ea if r[7] == "WON")))
# Slithery Fight: what do the others do at the coiled start, and how long does the queen live?
P("\nSlithery Fight (the queen starts as a 25-long coil): first action of each queen and her fate")
for name, pred in (("meow", lambda g, s: g[s] == X.ME), ("Vibing++", lambda g, s: g[s] == X.VIB), ("SSS", lambda g, s: g[s] == X.SSS), ("forgot", lambda g, s: g[s] == X.FORGOT),
                   ("test4", lambda g, s: g[s] == X.T4), ("WeHaveQuizzes", lambda g, s: g[s] == X.WHQ)):
    c = Counter(); n = 0; dr = []; alive = 0; won = 0
    for g in gs:
        if g["map"] != "Slithery Fight":
            continue
        for side in "AB":
            if not pred(g, side):
                continue
            d = g["d"]
            n += 1
            sp = [s for s in d["splits"] if s["side"] == side and s["r"] <= 5]
            if sp:
                s0 = sp[0]
                c["first split keeps %s, child %s" % (s0["keep"] if s0["keep"] <= 3 else "4+", s0["child"] if s0["child"] <= 3 else "4+")] += 1
            else:
                c["no split in rounds 0-5"] += 1
            qd = d["qdeath"].get(side)
            if qd: dr.append(qd["r"])
            else: alive += 1
            won += X.won(g, side)
    if n:
        dr.sort()
        P("   %-14s games %-3d %s | queen dead by round 10: %d, by round 100: %d, alive at the end: %d | games won %d" % (
            name, n, dict(c), sum(1 for r in dr if r <= 10), sum(1 for r in dr if r <= 100), alive, won))
