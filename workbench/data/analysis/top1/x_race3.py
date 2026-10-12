#!/usr/bin/env python3
"""What decides a round-500 game with both queens dead: the total length or the longest dragon, and how early?
Logistic fits of win on log(own/enemy total length) and log(own/enemy longest dragon) at rounds 300 and 400, by
map class and team group. Then the trade candidate 3 makes on maps over 1,200 cells, priced with those fits:
total length at round 300 up by 15 or 25%, the longest dragon at round 300 or 400 down to what it is on the
smaller maps. Own code on x_out/c1/. Output: x_out/race3.txt"""
import math
from collections import Counter
import x_load as X
import x_logit as LG
out = open("x_out/race3.txt", "w")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.write(s + "\n")
gs = [g for g in X.games("c1") if g["d"] and X.is_csv(g)]
def rows(pred, cpred, R, only_dd=True):
    res = []
    for g in gs:
        if not cpred(g):
            continue
        for side in "AB":
            if not X.in_study(g, side) or not pred(g, side):
                continue
            d = g["d"]; es = X.other(side); e = d["end"]
            if e["rounds"] < 500:
                continue
            if only_dd and (e["qalive"][side] or e["qalive"][es]):
                continue
            o, en = X.stats_at(d, R, side), X.stats_at(d, R, es)
            if not o or not en or not en[1] or not o[1]:
                continue
            res.append(dict(win=1.0 if X.won(g, side) else 0.0, lt=math.log(o[1] / en[1]), ll=math.log(max(2, o[2]) / max(2, en[2])),
                            ol=o[2], el=en[2], ot=o[1], et=en[1], g=g, side=side))
    return res
BIG = lambda g: g["cells"] > 1200
SMALL = lambda g: g["cells"] <= 1200
ANY = lambda g: True
fits = {}
for cname, cpred in (("maps over 1,200 cells", BIG), ("maps of 1,200 cells or fewer", SMALL), ("all maps", ANY)):
    for name, pred in (("meow", lambda g, s: g[s] == X.ME), ("top three", lambda g, s: g[s] in X.TOP3),
                       ("every side rated 2000+ or meow", lambda g, s: True)):
        for R in (300, 400):
            rs = rows(pred, cpred, R)
            if len(rs) < 25 or sum(r["win"] for r in rs) < 5:
                continue
            Xm = [[1.0, r["lt"], r["ll"]] for r in rs]
            y = [r["win"] for r in rs]
            beta, se = LG.fit(Xm, y)
            fits[(cname, name, R)] = (beta, rs)
            P("%-30s %-32s round %d: n=%-4d won %-4d | const %+.2f (se %.2f)  log total ratio %+.2f (se %.2f)  log longest ratio %+.2f (se %.2f)" % (
                cname, name, R, len(rs), sum(y), beta[0], se[0], beta[1], se[1], beta[2], se[2]))
P("\n== Candidate 3's trade on maps over 1,200 cells, priced on OUR round-500 both-dead games there")
P("   (what our longest dragon is on the smaller maps, where the leader rules start at round 300: medians)")
sm = rows(lambda g, s: g[s] == X.ME, SMALL, 300)
bg = rows(lambda g, s: g[s] == X.ME, BIG, 300)
sm4 = rows(lambda g, s: g[s] == X.ME, SMALL, 400)
bg4 = rows(lambda g, s: g[s] == X.ME, BIG, 400)
def med(v):
    v = sorted(v); return v[len(v) // 2]
P("   our longest at round 300: big maps %d, smaller maps %d; at round 400: big %d, smaller %d" % (
    med([r["ol"] for r in bg]), med([r["ol"] for r in sm]), med([r["ol"] for r in bg4]), med([r["ol"] for r in sm4])))
for key in (("maps over 1,200 cells", "meow", 300), ("maps over 1,200 cells", "every side rated 2000+ or meow", 300),
            ("all maps", "every side rated 2000+ or meow", 300), ("maps over 1,200 cells", "meow", 400),
            ("maps over 1,200 cells", "every side rated 2000+ or meow", 400), ("all maps", "every side rated 2000+ or meow", 400)):
    if key not in fits:
        continue
    beta, _ = fits[key]
    R = key[2]
    base = bg if R == 300 else bg4
    now = sum(LG.predict(beta, [1.0, r["lt"], r["ll"]]) for r in base)
    P("   fit of %s / %s / round %d on our %d big-map both-dead games: model wins now %.1f (real %d)" % (key[0], key[1], R, len(base), now, sum(r["win"] for r in base)))
    small_long = med([r["ol"] for r in (sm if R == 300 else sm4)])
    for up in (0.15, 0.25):
        for lab, f in (("leader unchanged", lambda ol: ol), ("leader halfway to the small-map length", lambda ol: (ol + min(ol, small_long)) / 2.0),
                       ("leader as on the smaller maps (%d)" % small_long, lambda ol: min(ol, small_long))):
            w = sum(LG.predict(beta, [1.0, r["lt"] + math.log(1 + up), math.log(max(2, f(r["ol"])) / max(2, r["el"]))]) for r in base)
            P("      total length +%d%%, %-42s -> %.1f wins (%+.1f)" % (100 * up, lab, w, w - now))
