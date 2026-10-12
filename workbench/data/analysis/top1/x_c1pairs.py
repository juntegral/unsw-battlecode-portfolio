#!/usr/bin/env python3
"""Old/new pairs of every smoke run: did OUR queen die earlier or later in the new build (same opponent, same map)?
Own code on x_out/c1/. Output: x_out/c1pairs.txt"""
from collections import Counter

import x_load as X

out = open("x_out/c1pairs.txt", "w")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


gs = [g for g in X.games("c1") if g["d"]]
mine = [(g, X.side_of(g, X.ME)) for g in gs if X.side_of(g, X.ME)]


def pairs(old, new):
    a = {(X.opp(g, s)[0], g["map"]): (g, s) for g, s in mine if g["set"] == old and g["map"] != "Schooltime"}
    b = {(X.opp(g, s)[0], g["map"]): (g, s) for g, s in mine if g["set"] == new and g["map"] != "Schooltime"}
    c = Counter()
    do, dn = [], []
    for k in set(a).intersection(b):
        (g0, s0), (g1, s1) = a[k], b[k]
        r0 = g0["d"]["qdeath"].get(s0, {}).get("r", 501)
        r1 = g1["d"]["qdeath"].get(s1, {}).get("r", 501)
        do.append(r0)
        dn.append(r1)
        c["earlier in new" if r1 < r0 else "later in new" if r1 > r0 else "same"] += 1
    do.sort()
    dn.sort()
    P("%-20s against %-20s pairs %-3d our queen: %s | median death round old %d, new %d" % (
        old, new, len(do), dict(c), do[len(do) // 2] if do else -1, dn[len(dn) // 2] if dn else -1))


for old, new in (("qh31-test-old", "qh31-test-new"), ("qh31b-test-old", "qh31b-test-new"), ("qh31b-dev1-old", "qh31b-dev1-new"),
                 ("stride-old", "stride-new"), ("passage2-test-old", "passage2-test-new"), ("tc30-dev1-old", "tc30-dev1b-new"),
                 ("qh31-test-old", "tc30-test-new"), ("qh31b-test-old", "qn23-test-new"), ("qh31-test-old", "qh31b-test-old"),
                 ("stride-old", "passage2-test-old")):
    pairs(old, new)
