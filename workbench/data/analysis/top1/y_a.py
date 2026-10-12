#!/usr/bin/env python3
"""Claim A: the footing of the longest-dragon race. Reads y_out/w1. Output: y_out/a.txt

A "race" = a game that reaches round 500 with both queens dead (the longest single dragon wins).
Footings compared at round R: T = total length; P = potential (longest + ceil(L/2) of every other own dragon);
D = a fitted "what a side usually makes of it" footing: final longest ~ a*longest + k*rest, per map class.
"""
import math
import random
import sys

import y_lib as Y
import y_r as R

OUTF = open(Y.out_path("a.txt"), "w")


def pr(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUTF.write(s + "\n")


w1 = R.load_w1()
recs = R.sides(w1)
races = [r for r in recs if r["race"]]
pr("games walked:", len(w1), "| game-sides:", len(recs), "| races:", len(races))

GROUPS = ["meow", "opp", "Vibing++", "SSS", "forgot"]


def sel(group, pred=None):
    if group == "top3":
        out = [r for r in races if r["group"] in ("Vibing++", "SSS", "forgot")]
    elif group == "live":
        out = [r for r in races if r["group"] == "meow" and r["build"] == "live"]
    elif group == "test":
        out = [r for r in races if r["group"] == "meow" and r["build"] == "test"]
    else:
        out = [r for r in races if r["group"] == group]
    if pred:
        out = [r for r in out if pred(r)]
    return out


def wl(rs):
    return "%d of %d" % (sum(r["won"] for r in rs), len(rs))


def wlp(rs):
    n = len(rs)
    k = sum(r["won"] for r in rs)
    if n == 0:
        return "0 of 0"
    lo, hi = Y.wilson(k, n)
    return "%d of %d = %.0f%% (%.0f-%.0f)" % (k, n, 100.0 * k / n, 100 * lo, 100 * hi)


BANDS = [(0, 0.5, "under 0.5"), (0.5, 0.8, "0.5-0.8"), (0.8, 1.25, "0.8-1.25"), (1.25, 1e9, "over 1.25")]


def band_of(x):
    for lo, hi, name in BANDS:
        if lo <= x < hi:
            return name
    return None


def bandrow(rs, rnd, key):
    cells = []
    for lo, hi, name in BANDS:
        sub = [r for r in rs if R.ratio(r, rnd, key) is not None and lo <= R.ratio(r, rnd, key) < hi]
        cells.append(wl(sub))
    return " | ".join(cells)


small = lambda r: not r["big"]  # noqa: E731
big = lambda r: r["big"]  # noqa: E731
vs_t4 = lambda r: r["oteam"] == Y.T4  # noqa: E731
vs_whq = lambda r: r["oteam"] == Y.WHQ  # noqa: E731
vs_both = lambda r: r["oteam"] in (Y.T4, Y.WHQ)  # noqa: E731

pr("\n== 1. Races and wins (theirs: lead 143/41, 447/266; A5 96+47, 154/85, 141/82, 152/99)")
for gname in ["meow", "live", "test", "opp", "Vibing++", "SSS", "forgot", "top3"]:
    rs = sel(gname)
    pr("  %-9s races %s | small maps %s | big maps %s | vs test4 %s | vs WHQ %s" % (
        gname, wl(rs), wl([r for r in rs if small(r)]), wl([r for r in rs if big(r)]),
        wl([r for r in rs if vs_t4(r)]), wl([r for r in rs if vs_whq(r)])))

pr("\n== 2. By own / enemy TOTAL length at round 400 (bands: %s)" % ", ".join(b[2] for b in BANDS))
pr("   theirs (redteam.md): small maps level meow 9 of 30, top three 22 of 40; ahead 15 of 18 / 77 of 83; big maps behind 6 of 23 / 17 of 49, level 4 of 6 / 73 of 116")
for gname in ["meow", "live", "test", "opp", "top3", "Vibing++", "SSS", "forgot"]:
    rs = sel(gname)
    pr("  %-9s small: %s" % (gname, bandrow([r for r in rs if small(r)], 400, "total")))
    pr("  %-9s big:   %s" % ("", bandrow([r for r in rs if big(r)], 400, "total")))
for gname, pred, lab in [("meow", vs_t4, "meow vs test4"), ("meow", vs_whq, "meow vs WHQ"), ("top3", vs_t4, "top3 vs test4"),
                         ("top3", vs_whq, "top3 vs WHQ")]:
    rs = sel(gname, pred)
    pr("  %-14s small: %s || big: %s" % (lab, bandrow([r for r in rs if small(r)], 400, "total"),
                                           bandrow([r for r in rs if big(r)], 400, "total")))

pr("\n== 3. By own / enemy POTENTIAL at rounds 300, 350, 400, all maps (theirs, deep-read-5 2.0: meow at 300: 0 of 48 | 20 of 58 | 11 of 23 | 10 of 14; at 350 level 12 of 24; at 400 level 13 of 34; top three 5 of 43 | 18 of 51 | 99 of 169 | 144 of 184; 103 of 178; 89 of 155)")
for rnd in (300, 350, 400):
    pr(" round %d" % rnd)
    for gname in ["meow", "live", "test", "opp", "top3", "Vibing++", "SSS", "forgot"]:
        rs = sel(gname)
        pr("  %-9s all: %s || small: %s || big: %s" % (
            gname, bandrow(rs, rnd, "P"), bandrow([r for r in rs if small(r)], rnd, "P"),
            bandrow([r for r in rs if big(r)], rnd, "P")))
    for gname, pred, lab in [("meow", vs_t4, "meow vs test4"), ("meow", vs_whq, "meow vs WHQ"),
                             ("meow", lambda r: not vs_both(r), "meow vs others"),
                             ("top3", vs_t4, "top3 vs test4"), ("top3", vs_whq, "top3 vs WHQ"),
                             ("top3", vs_both, "top3 vs both"),
                             ("SSS", vs_both, "SSS vs both"), ("Vibing++", vs_both, "Vib vs both"), ("forgot", vs_both, "forgot vs both")]:
        rs = sel(gname, pred)
        pr("  %-15s all: %s || small: %s || big: %s" % (lab, bandrow(rs, rnd, "P"),
                                                        bandrow([r for r in rs if small(r)], rnd, "P"),
                                                        bandrow([r for r in rs if big(r)], rnd, "P")))

pr("\n== 3b. The same by TOTAL length at rounds 250 and 300 (before most feeding), all maps / small / big")
for rnd in (250, 300):
    pr(" round %d" % rnd)
    for gname in ["meow", "opp", "top3"]:
        rs = sel(gname)
        pr("  %-9s all: %s || small: %s || big: %s" % (
            gname, bandrow(rs, rnd, "total"), bandrow([r for r in rs if small(r)], rnd, "total"),
            bandrow([r for r in rs if big(r)], rnd, "total")))
    for gname, pred, lab in [("meow", vs_both, "meow vs t4+WHQ"), ("top3", vs_both, "top3 vs t4+WHQ")]:
        rs = sel(gname, pred)
        pr("  %-15s all: %s || small: %s || big: %s" % (lab, bandrow(rs, rnd, "total"),
                                                        bandrow([r for r in rs if small(r)], rnd, "total"),
                                                        bandrow([r for r in rs if big(r)], rnd, "total")))

pr("\n== 4. How we enter our races (theirs: median P ratio at 300 0.62; 106 of 143 below 0.8, 20 won; 48 under 0.5, 0 won)")
for gname in ["meow", "live", "test", "opp", "top3"]:
    rs = sel(gname)
    xs = [R.ratio(r, 300, "P") for r in rs if R.ratio(r, 300, "P") is not None]
    below = [r for r in rs if R.ratio(r, 300, "P") is not None and R.ratio(r, 300, "P") < 0.8]
    ts = [R.ratio(r, 300, "total") for r in rs if R.ratio(r, 300, "total") is not None]
    pr("  %-9s median P ratio at 300 %.2f | below 0.8: %d of %d, won %d | median total ratio at 300 %.2f" % (
        gname, Y.med(xs), len(below), len(rs), sum(r["won"] for r in below), Y.med(ts)))

pr("\n== 5. Inside the first red team's band: small maps, own / enemy total at round 400 in 0.8-1.25")
pr("   theirs (deep-read-5): meow 30 games 9 won, total at 300 65.5 : 90.5, P at 300 39.5 : 54, enemy over 1.25x ours at 300 in 17 (won 5); top three 40, 22, 101 : 94, 61.5 : 56, 7 (won 5)")
for gname in ["meow", "live", "test", "top3", "opp"]:
    rs = [r for r in sel(gname, small) if R.ratio(r, 400, "total") is not None and 0.8 <= R.ratio(r, 400, "total") < 1.25]
    if not rs:
        continue
    def md(rnd, key, own):
        return Y.med([R.snap(r, rnd, key, own) for r in rs])
    far = [r for r in rs if R.ratio(r, 300, "total") < 0.8]
    lev = [r for r in rs if 0.8 <= R.ratio(r, 300, "total") < 1.25]
    ahead = [r for r in rs if R.ratio(r, 300, "total") >= 1.25]
    pr("  %-6s %s | total at 300 %s : %s, at 350 %s : %s, at 400 %s : %s | P at 300 %s : %s | longest at 400 %s : %s | units at 400 %s : %s" % (
        gname, wl(rs), md(300, "total", True), md(300, "total", False), md(350, "total", True), md(350, "total", False),
        md(400, "total", True), md(400, "total", False), md(300, "P", True), md(300, "P", False),
        md(400, "L", True), md(400, "L", False), md(400, "units", True), md(400, "units", False)))
    pr("         by total ratio at round 300: under 0.8 %s | 0.8-1.25 %s | over 1.25 %s ;  by P ratio at 300: %s" % (
        wl(far), wl(lev), wl(ahead), bandrow(rs, 300, "P")))

# ---------------------------------------------------------------------------------------------------------------
pr("\n== 6. Which footing tells who wins? Logistic fit win ~ c + b*ln(own/enemy), per group. c = the group's edge at ratio 1")
pr("   (c in log-odds; 'at level' = win chance at ratio 1; 'll/n' = mean log-likelihood, nearer 0 is a better footing)")


def fit(rs, rnd, key, extra=None):
    X, y = [], []
    for r in rs:
        v = R.ratio(r, rnd, key) if not callable(key) else key(r, rnd)
        if v is None or v <= 0:
            continue
        X.append([1.0, math.log(v)])
        y.append(1 if r["won"] else 0)
    if len(X) < 8 or sum(y) in (0, len(y)):
        return None
    beta, cov, ll = Y.logit_fit(X, y, ridge=1e-4)
    return dict(c=beta[0], b=beta[1], se_c=math.sqrt(max(0.0, cov[0][0])), se_b=math.sqrt(max(0.0, cov[1][1])), n=len(X),
                ll=ll / len(X), X=X, y=y)


# fitted footing D: final longest ~ a*L + k*rest, per map class, from every side of every race game
def all_sides_of_races():
    seen = set()
    rows = []
    for r in races:
        if r["gid"] in seen:
            continue
        seen.add(r["gid"])
        for s in "AB":
            rows.append((r["w"], s, r["big"]))
    return rows


DCOEF = {}
for rnd in (300, 350, 400, 450):
    for cls in (False, True):
        sxx = sxy = syy = sxz = syz = 0.0
        n = 0
        for w, s, isbig in all_sides_of_races():
            if isbig != cls:
                continue
            sn = w["snap"].get(str(rnd))
            if not sn:
                continue
            L = sn[s][R.IX["L"]]
            rest = sn[s][R.IX["P"]] - L
            fin = w["snap"]["end"][s][R.IX["L"]]
            sxx += L * L
            sxy += L * rest
            syy += rest * rest
            sxz += L * fin
            syz += rest * fin
            n += 1
        det = sxx * syy - sxy * sxy
        a = (sxz * syy - syz * sxy) / det
        k = (sxx * syz - sxy * sxz) / det
        DCOEF[(rnd, cls)] = (a, k, n)
pr("   fitted footing D = a*longest + k*(pearls the others would drop), from all %d sides of race games:" % len(all_sides_of_races()))
for rnd in (300, 350, 400, 450):
    pr("     round %d: small maps a=%.2f k=%.2f (n=%d) | big maps a=%.2f k=%.2f (n=%d)" % (
        (rnd,) + DCOEF[(rnd, False)] + DCOEF[(rnd, True)]))


def Dval(w, s, rnd, isbig):
    sn = w["snap"].get(str(rnd))
    if not sn:
        return None
    a, k, _ = DCOEF[(rnd, isbig)]
    L = sn[s][R.IX["L"]]
    return a * L + k * (sn[s][R.IX["P"]] - L)


def Dratio(r, rnd):
    a = Dval(r["w"], r["side"], rnd, r["big"])
    b = Dval(r["w"], r["oside"], rnd, r["big"])
    if a is None or not b:
        return None
    return a / b


def Plocratio(r, rnd):
    return R.ratio(r, rnd, "Ploc")


FOOT = [("T250", 250, "total"), ("T300", 300, "total"), ("T350", 350, "total"), ("T400", 400, "total"),
        ("P250", 250, "P"), ("P300", 300, "P"), ("P350", 350, "P"), ("P400", 400, "P"),
        ("D300", 300, Dratio), ("D350", 350, Dratio), ("D400", 400, Dratio),
        ("Pl400", 400, Plocratio), ("L400", 400, "L")]

for gname, pred, lab in [("meow", None, "meow, all races"), ("meow", small, "meow, small maps"), ("meow", big, "meow, big maps"),
                         ("meow", vs_both, "meow vs test4+WHQ"),
                         ("top3", None, "top three, all"), ("top3", small, "top three, small"), ("top3", big, "top three, big"),
                         ("top3", vs_both, "top three vs test4+WHQ"), ("opp", None, "our opponents (mirror)")]:
    rs = sel(gname, pred)
    pr("  %s (%s)" % (lab, wl(rs)))
    for name, rnd, key in FOOT:
        f = fit(rs, rnd, key)
        if not f:
            pr("     %-6s (no fit)" % name)
            continue
        pr("     %-6s n=%3d  c=%+.2f (se %.2f)  -> at level %.0f%% (%.0f-%.0f)  b=%.2f  ll/n=%.3f" % (
            name, f["n"], f["c"], f["se_c"], 100 * Y.sigmoid(f["c"]), 100 * Y.sigmoid(f["c"] - 1.2816 * f["se_c"]),
            100 * Y.sigmoid(f["c"] + 1.2816 * f["se_c"]), f["b"], f["ll"]))

# ---------------------------------------------------------------------------------------------------------------
pr("\n== 7. What our races would have given at somebody else's conversion: reference curve applied to OUR ratios")
pr("   (reference = a logistic curve fitted on the reference group's races; range = 10th-90th percentile over 300")
pr("    bootstrap refits of the reference, to which the chance in our own 143 outcomes must still be added)")
random.seed(7)


def expected(ref_rs, tgt_rs, rnd, key, nboot=300):
    f = fit(ref_rs, rnd, key)
    if not f:
        return None
    def apply(c, b):
        tot = 0.0
        n = 0
        for r in tgt_rs:
            v = R.ratio(r, rnd, key) if not callable(key) else key(r, rnd)
            if v is None or v <= 0:
                continue
            tot += Y.sigmoid(c + b * math.log(v))
            n += 1
        return tot, n
    e, n = apply(f["c"], f["b"])
    bs = []
    X, y = f["X"], f["y"]
    m = len(X)
    for _ in range(nboot):
        idx = [random.randrange(m) for _ in range(m)]
        yy = [y[i] for i in idx]
        if sum(yy) in (0, m):
            continue
        try:
            bb, _, _ = Y.logit_fit([X[i] for i in idx], yy, ridge=1e-4, iters=25)
        except ValueError:
            continue
        bs.append(apply(bb[0], bb[1])[0])
    bs.sort()
    lo = bs[int(0.1 * len(bs))]
    hi = bs[int(0.9 * len(bs))]
    return e, lo, hi, n, f


def show(lab, ref_rs, tgt_rs, foots):
    act = sum(r["won"] for r in tgt_rs)
    pr("  %s: our actual %d of %d; reference %s" % (lab, act, len(tgt_rs), wl(ref_rs)))
    for name, rnd, key in foots:
        res = expected(ref_rs, tgt_rs, rnd, key)
        if not res:
            pr("     %-6s no fit" % name)
            continue
        e, lo, hi, n, f = res
        # chance in our own outcomes: sd of a sum of n coin flips with the predicted chances ~ sqrt(sum p(1-p)); use e/n
        p = e / n
        sd = math.sqrt(n * p * (1 - p))
        pr("     %-6s expected %.1f (%.1f to %.1f) of %d -> gap %+.1f wins (reference c=%+.2f b=%.2f); chance sd of our own count %.1f" % (
            name, e, lo, hi, n, e - act, f["c"], f["b"], sd))


F7 = [("T250", 250, "total"), ("T300", 300, "total"), ("P300", 300, "P"), ("P350", 350, "P"), ("D300", 300, Dratio),
      ("D350", 350, Dratio), ("T400", 400, "total"), ("P400", 400, "P"), ("D400", 400, Dratio)]
me_all = sel("meow")
show("all our races, top three's curve (all their opponents)", sel("top3"), me_all, F7)
show("all our races, top three's curve vs test4+WHQ only", sel("top3", vs_both), me_all, F7)
show("our races vs test4+WHQ, top three's curve vs test4+WHQ", sel("top3", vs_both), sel("meow", vs_both), F7)
show("our small-map races, top three's small-map curve", sel("top3", small), sel("meow", small), F7)
show("our big-map races, top three's big-map curve", sel("top3", big), sel("meow", big), F7)
show("our small-map races vs t4+WHQ, top three small vs t4+WHQ", sel("top3", lambda r: small(r) and vs_both(r)),
     sel("meow", lambda r: small(r) and vs_both(r)), F7)
show("our races, our own opponents' curve (the mirror: what test4/WHQ make of the same ratio against us)", sel("opp"), me_all, F7)
show("live bot only, top three's curve", sel("top3"), sel("live"), F7)
rt = [r for r in sel("meow", small) if R.ratio(r, 400, "total") is not None and 0.8 <= R.ratio(r, 400, "total") < 1.25]
show("the first red team's 30 games (small maps, level total at 400), top three's small-map curve", sel("top3", small), rt, F7)
show("the first red team's 30 games, top three's curve vs test4+WHQ (all maps)", sel("top3", vs_both), rt, F7)

# ---------------------------------------------------------------------------------------------------------------
pr("\n== 8. Level bands on the alternative footings (0.8-1.25): won of games")
for name, rnd, key in [("T300", 300, "total"), ("P300", 300, "P"), ("D300", 300, Dratio), ("P350", 350, "P"), ("D350", 350, Dratio),
                       ("T400", 400, "total"), ("P400", 400, "P"), ("D400", 400, Dratio), ("Pl400", 400, Plocratio)]:
    def lev(rs):
        out = []
        for r in rs:
            v = R.ratio(r, rnd, key) if not callable(key) else key(r, rnd)
            if v is not None and 0.8 <= v < 1.25:
                out.append(r)
        return out
    pr("  %-6s meow %s | small %s | big %s | vs t4+WHQ %s || top3 %s | small %s | big %s | vs t4+WHQ %s || opp %s" % (
        name, wlp(lev(sel("meow"))), wl(lev(sel("meow", small))), wl(lev(sel("meow", big))), wl(lev(sel("meow", vs_both))),
        wlp(lev(sel("top3"))), wl(lev(sel("top3", small))), wl(lev(sel("top3", big))), wl(lev(sel("top3", vs_both))),
        wl(lev(sel("opp")))))

pr("\n== 9. Completeness at the end (longest / potential), medians; and potential kept: P(end) / P(300)")
for gname in ["live", "test", "opp", "Vibing++", "SSS", "forgot"]:
    for cls, lab in ((False, "small"), (True, "big")):
        rs = [r for r in sel(gname) if r["big"] == cls]
        cs = [R.snap(r, "end", "L") / R.snap(r, "end", "P") for r in rs if R.snap(r, "end", "P")]
        fl = [R.snap(r, "end", "L") / R.snap(r, 300, "P") for r in rs if R.snap(r, 300, "P")]
        pr("  %-9s %-5s n=%3d completeness at end %.2f | final longest / P at 300 %.2f | P at 300/400/end %s/%s/%s" % (
            gname, lab, len(rs), Y.med(cs) or 0, Y.med(fl) or 0, Y.med([R.snap(r, 300, "P") for r in rs]),
            Y.med([R.snap(r, 400, "P") for r in rs]), Y.med([R.snap(r, "end", "P") for r in rs])))
OUTF.close()
