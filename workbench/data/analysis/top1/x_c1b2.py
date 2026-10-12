#!/usr/bin/env python3
"""Candidate 1, attack B continued: logistic fits of 'win' on 'first in-view chance taken', holding the economy at
that turn, the round, the own queen and the team fixed. Output: x_out/c1b2.txt"""
import math
import x_load as X
import x_logit as LG
out = open("x_out/c1b2.txt", "w")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.write(s + "\n")
gs = [g for g in X.games("c1") if g["d"] and X.is_csv(g)]
def rows(pred, maxL=12):
    res = []
    for g in gs:
        for side in "AB":
            if not X.in_study(g, side) or not pred(g, side):
                continue
            ch = [c for c in g["d"]["chances"] if c["side"] == side and not c.get("far") and c["cheb"] <= 3 and c.get("dS") is not None and c["L"] <= maxL]
            if not ch:
                continue
            c = ch[0]
            ratio = c["own"][1] / max(1, c["en"][1])
            res.append(dict(taken=1.0 if c["taken"] else 0.0, win=1.0 if X.won(g, side) else 0.0, lr=math.log(max(0.05, min(20, ratio))),
                            r=c["r"] / 100.0, oq=1.0 if c["oq"] > 0 else 0.0, team=g[side], L=c["L"],
                            outn=1.0 if c["own_h"] < c["en_h"] else 0.0, units=math.log(max(1, c["own"][0]) / max(1, c["en"][0]))))
    return res
def run(label, rs, with_team=False, extra=()):
    teams = sorted({r["team"] for r in rs}) if with_team else []
    names = ["const", "taken", "log length ratio", "round/100", "own queen alive"] + list(extra) + ["team %s" % t for t in teams[1:]]
    Xm = []
    for r in rs:
        v = [1.0, r["taken"], r["lr"], r["r"], r["oq"]] + [r[e] for e in extra] + [1.0 if r["team"] == t else 0.0 for t in teams[1:]]
        Xm.append(v)
    y = [r["win"] for r in rs]
    beta, se = LG.fit(Xm, y)
    P("\n-- %s: n=%d, taken %d, not taken %d" % (label, len(rs), sum(r["taken"] for r in rs), sum(1 - r["taken"] for r in rs)))
    for i in range(5 + len(extra)):
        P("   %-22s %+.2f (se %.2f)" % (names[i], beta[i], se[i]))
    def eff(b):
        tot = n = 0.0
        for v in Xm:
            if v[1] == 0.0:
                v1 = v[:]; v1[1] = 1.0
                tot += LG.predict(b, v1) - LG.predict(beta, v); n += 1
        return 100 * tot / max(1, n), n
    e, n = eff(beta)
    blo = beta[:]; blo[1] -= 1.2816 * se[1]
    bhi = beta[:]; bhi[1] += 1.2816 * se[1]
    P("   average change in win chance for the NOT-taken games if taken: %+.1f points (80%% interval %+.1f to %+.1f), n=%d -> %+.1f games" % (e, eff(blo)[0], eff(bhi)[0], n, e * n / 100))
me = rows(lambda g, s: g[s] == X.ME)
fg = rows(lambda g, s: g[s] == X.FORGOT)
ot = rows(lambda g, s: g[s] not in (X.ME,) + X.TOP3 and g[s + "e"] >= 2000)
run("meow (401 games)", me)
run("meow, adding 'outnumbered where it stands' and the unit ratio", me, extra=("outn", "units"))
run("forgot", fg)
run("forgot, adding 'outnumbered' and the unit ratio", fg, extra=("outn", "units"))
run("other teams rated 2000+", ot, with_team=True)
run("pooled meow + forgot + others, team terms", me + fg + ot, with_team=True)
run("pooled, adding 'outnumbered' and the unit ratio", me + fg + ot, with_team=True, extra=("outn", "units"))
