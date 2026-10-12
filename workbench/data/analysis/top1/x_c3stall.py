#!/usr/bin/env python3
"""Candidate 3, a natural experiment inside our own games: does our economy stall after the leader rules start?
On maps over 1,200 cells they start at round 150, on the others at round 300. Same games throughout each row
(only games that reach the last round of the row), means; own : enemy. Own code on x_out/c1/. Output: x_out/c3stall.txt"""
import x_load as X
out = open("x_out/c3stall.txt", "w")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.write(s + "\n")
gs = [g for g in X.games("c1") if g["d"] and X.is_csv(g)]
def table(label, pred, rounds):
    rows = []
    for g in gs:
        for side in "AB":
            if not pred(g, side):
                continue
            o = X.other(side)
            if not (X.in_study(g, side) or (g[o] == X.ME and X.in_study(g, o))):
                continue
            d = g["d"]
            st = [(X.stats_at(d, R, side), X.stats_at(d, R, o)) for R in rounds]
            if any(a is None or b is None for a, b in st):
                continue
            rows.append(st)
    n = len(rows)
    if not n:
        return
    line = "   %-44s n=%-4d" % (label, n)
    for i, R in enumerate(rounds):
        u = sum(r[i][0][0] for r in rows) / n; t = sum(r[i][0][1] for r in rows) / n; lg = sum(r[i][0][2] for r in rows) / n
        eu = sum(r[i][1][0] for r in rows) / n; et = sum(r[i][1][1] for r in rows) / n
        line += " | r%d: units %.0f:%.0f total %.0f:%.0f longest %.0f" % (R, u, eu, t, et, lg)
    P(line)
BIG = lambda g: g["cells"] > 1200
P("== maps over 1,200 cells (our leader rules from round 150), games that reach round 300")
for lab, pred in (("meow live", lambda g, s: BIG(g) and g[s] == X.ME and X.build(g) == "live"), ("meow tc30 build", lambda g, s: BIG(g) and g[s] == X.ME and X.build(g) == "tc30"),
                  ("our opponents", lambda g, s: BIG(g) and g[X.other(s)] == X.ME), ("top three", lambda g, s: BIG(g) and g[s] in X.TOP3)):
    table(lab, pred, (100, 150, 200, 250, 300))
P("== maps of 1,200 cells or fewer (our leader rules from round 300), games that reach round 400")
for lab, pred in (("meow live", lambda g, s: not BIG(g) and g[s] == X.ME and X.build(g) == "live"),
                  ("our opponents (of the live bot)", lambda g, s: not BIG(g) and g[X.other(s)] == X.ME and X.build(g) == "live"),
                  ("top three", lambda g, s: not BIG(g) and g[s] in X.TOP3)):
    table(lab, pred, (150, 200, 250, 300, 350, 400))
P("== the same split by whether we were ahead in total length at round 300 (smaller maps, live bot)")
def ahead(g, s):
    d = g["d"]; a, b = X.stats_at(d, 300, s), X.stats_at(d, 300, X.other(s))
    return a and b and a[1] >= b[1]
table("meow live, ahead or level at round 300", lambda g, s: not BIG(g) and g[s] == X.ME and X.build(g) == "live" and ahead(g, s), (200, 250, 300, 350, 400))
table("meow live, behind at round 300", lambda g, s: not BIG(g) and g[s] == X.ME and X.build(g) == "live" and not ahead(g, s), (200, 250, 300, 350, 400))
P("== maps over 1,200 cells, live bot, by whether we had 56 or more units at round 150 (then early feeding can start at round 200)")
def u56(g, s):
    a = X.stats_at(g["d"], 150, s)
    return a and a[0] >= 56
table("meow live, 56+ units at round 150", lambda g, s: BIG(g) and g[s] == X.ME and X.build(g) == "live" and u56(g, s), (100, 150, 200, 250, 300))
table("meow live, fewer than 56 units at round 150", lambda g, s: BIG(g) and g[s] == X.ME and X.build(g) == "live" and not u56(g, s), (100, 150, 200, 250, 300))
