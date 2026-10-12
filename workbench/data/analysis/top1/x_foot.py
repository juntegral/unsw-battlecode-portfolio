#!/usr/bin/env python3
"""Attack on the footing (I): how solid are the band win rates, what the footing leaves out, and where our games go.
Own code on x_out/c1/. Output: x_out/foot.txt"""
from collections import Counter, defaultdict
import x_load as X
out = open("x_out/foot.txt", "w")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.write(s + "\n")
gs = [g for g in X.games("c1") if g["d"] and X.is_csv(g)]
def collect(pred):
    band = [[0, 0] for _ in range(4)]
    early = [0, 0]
    n = w = 0
    for g in gs:
        for side in "AB":
            if not X.in_study(g, side) or not pred(g, side):
                continue
            d = g["d"]; es = X.other(side)
            n += 1; w += X.won(g, side)
            o, e = X.stats_at(d, 300, side), X.stats_at(d, 300, es)
            if d["end"]["rounds"] <= 300 or not o or not e or not e[1] or not o[1]:
                early[0] += X.won(g, side); early[1] += 1
                continue
            b = X.band(o[1] / e[1])
            band[b][0] += X.won(g, side); band[b][1] += 1
    return n, w, band, early
me = collect(lambda g, s: g[s] == X.ME)
top = collect(lambda g, s: g[s] in X.TOP3)
for name, (n, w, band, early) in (("meow", me), ("top three", top)):
    P("%s: %d games, won %d; over before round 300: %s; by band at round 300:" % (name, n, w, X.frac(early[0], early[1])))
    for b in range(4):
        lo, hi = X.wilson(band[b][0], band[b][1])
        P("   %-8s %-18s 80%% range %.0f-%.0f%%" % (X.BAND_NAMES[b], X.frac(band[b][0], band[b][1]), 100 * lo, 100 * hi))
nme = sum(b[1] for b in me[2]); ntop = sum(b[1] for b in top[2])
# what-ifs with ranges
our_rate = [b[0] / b[1] for b in me[2]]; top_rate = [b[0] / b[1] for b in top[2]]
our_mix = [b[1] / nme for b in me[2]]; top_mix = [b[1] / ntop for b in top[2]]
now = sum(b[0] for b in me[2])
conv = sum(nme * our_mix[i] * top_rate[i] for i in range(4))
econ = sum(nme * top_mix[i] * our_rate[i] for i in range(4))
lo = sum(nme * top_mix[i] * X.wilson(me[2][i][0], me[2][i][1])[0] for i in range(4))
hi = sum(nme * top_mix[i] * X.wilson(me[2][i][0], me[2][i][1])[1] for i in range(4))
clo = sum(nme * our_mix[i] * X.wilson(top[2][i][0], top[2][i][1])[0] for i in range(4))
chi = sum(nme * our_mix[i] * X.wilson(top[2][i][0], top[2][i][1])[1] for i in range(4))
P("\nour %d games that reach round 300: won %d" % (nme, now))
P("   'conversion' what-if (their band rates, our mix of bands): %.1f wins (%+.1f); with the 80%% ranges of their rates: %.0f to %.0f" % (conv, conv - now, clo, chi))
P("   'economy' what-if (our band rates, their mix of bands): %.1f wins (%+.1f); with the 80%% ranges of OUR rates: %.0f to %.0f (%+.0f to %+.0f)" % (econ, econ - now, lo, hi, lo - now, hi - now))
P("   share of the economy what-if that rests on our two upper bands (%d and %d games): %.0f of %.1f wins" % (
    me[2][2][1], me[2][3][1], sum(nme * top_mix[i] * our_rate[i] for i in (2, 3)), econ))
# where games go
P("\nHow our 401 games end, with the round of the end for wipe-outs:")
c = Counter()
for g in gs:
    side = X.side_of(g, X.ME)
    if side is None or not X.in_study(g, side):
        continue
    d = g["d"]; e = d["end"]; es = X.other(side)
    big = "big" if g["cells"] > 1200 else "small"
    if e["rounds"] < 500:
        k = "wipe-out before r300" if e["rounds"] <= 300 else "wipe-out r300+"
    else:
        k = "r500 own %s / her %s" % ("alive" if e["qalive"][side] else "dead", "alive" if e["qalive"][es] else "dead")
    c[k, "n"] += 1; c[k, "w"] += X.won(g, side)
    c[k, big, "n"] += 1; c[k, big, "w"] += X.won(g, side)
for k in ("wipe-out before r300", "wipe-out r300+", "r500 own dead / her dead", "r500 own dead / her alive", "r500 own alive / her alive", "r500 own alive / her dead"):
    P("   %-28s %-18s | maps over 1,200 cells %-14s | smaller maps %-14s" % (k, X.frac(c[k, "w"], c[k, "n"]),
      X.frac(c[k, "big", "w"], c[k, "big", "n"]), X.frac(c[k, "small", "w"], c[k, "small", "n"])))
