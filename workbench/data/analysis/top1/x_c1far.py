#!/usr/bin/env python3
"""Rams on a queen that my chance records do not show as an in-view strict chance: what are they?
Output: x_out/c1far.txt"""
from collections import Counter
import x_load as X
out = open("x_out/c1far.txt", "w")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.write(s + "\n")
gs = [g for g in X.games("c1") if g["d"] and X.is_csv(g) and g["map"] != "Schooltime"]
kinds = Counter(); ex = []
tot = 0
for g in gs:
    d = g["d"]
    for side in "AB":
        es = X.other(side)
        qd = d["qdeath"].get(es)
        if not (qd and qd["reason"] == "headon" and qd.get("actor_team") == side):
            continue
        tot += 1
        recs = [c for c in d["chances"] if c["side"] == side and c["a"] == qd["actor"] and c["r"] == qd["r"]]
        if not recs:
            kinds["no record at all"] += 1; ex.append((g["gid"], qd)); continue
        c = recs[-1]
        if c.get("far"):
            kinds["far record: start cheb %s" % ("<=3" if (c.get("cheb") or 9) <= 3 else ">3")] += 1
            if len(ex) < 12: ex.append((g["gid"], g["map"], c, qd))
            continue
        if c["cheb"] <= 3 and c.get("dS") is not None:
            kinds["in view, strict path (normal)"] += 1; continue
        if c["cheb"] <= 3:
            kinds["in view, NO strict path (dW %s)" % ("yes" if c.get("dW") is not None else "no")] += 1
            if len(ex) < 40: ex.append((g["gid"], g["map"], {k: c[k] for k in ("r", "a", "L", "R", "cheb", "manh", "dS", "dW", "n", "ate", "qL")}, qd.get("actor_steps")))
        else:
            kinds["NOT in view (cheb %d), strict path %s, steps %s" % (min(c["cheb"], 6), "yes" if c.get("dS") is not None else "no", "<=R" if c["n"] <= c["R"] else ">R")] += 1
            if len(ex) < 40: ex.append((g["gid"], g["map"], {k: c[k] for k in ("r", "a", "L", "R", "cheb", "manh", "dS", "dW", "n", "ate", "qL")}))
P("rams on a queen by the other team, all games (no Schooltime):", tot)
for k, v in kinds.most_common(): P("  %-60s %d" % (k, v))
for e in ex[:40]: P("  ", e)
