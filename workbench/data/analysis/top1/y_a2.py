#!/usr/bin/env python3
"""Claim A, part 2: where the race gap sits. Reads y_out/w1. Output: y_out/a2.txt

1. Fine bands of own / enemy potential at round 300: our record, the top three's, and what our races would give at
   the top three's rate band by band.
2. A pooled fit with a term for "this side is meow" (difference in the edge at level footing, and in the slope).
3. Check of medians: final longest / potential at round 300 (deep-read-5 says 0.65 for the live bot on small maps).
4. Timing: races by which side had started to convert by round 400 (longest / potential at 400).
"""
import math

import y_lib as Y
import y_r as R

OUTF = open(Y.out_path("a2.txt"), "w")


def pr(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUTF.write(s + "\n")


w1 = R.load_w1()
recs = [r for r in R.sides(w1) if r["race"]]
me = [r for r in recs if r["group"] == "meow"]
top = [r for r in recs if r["group"] in ("Vibing++", "SSS", "forgot")]
opp = [r for r in recs if r["group"] == "opp"]
small = lambda r: not r["big"]  # noqa: E731
big = lambda r: r["big"]  # noqa: E731

FB = [(0, 0.35), (0.35, 0.5), (0.5, 0.65), (0.65, 0.8), (0.8, 1.0), (1.0, 1.25), (1.25, 1.6), (1.6, 99)]


def table(title, a, b, rnd, key):
    pr("\n-- %s; footing %s at round %d" % (title, key, rnd))
    pr("   band        | meow won/games | top three won/games (rate) | meow at the top three's rate | gap")
    tot_e = tot_a = 0.0
    for lo, hi in FB:
        aa = [r for r in a if R.ratio(r, rnd, key) is not None and lo <= R.ratio(r, rnd, key) < hi]
        bb = [r for r in b if R.ratio(r, rnd, key) is not None and lo <= R.ratio(r, rnd, key) < hi]
        ka, kb = sum(r["won"] for r in aa), sum(r["won"] for r in bb)
        rate = kb / len(bb) if bb else 0.0
        e = rate * len(aa)
        tot_e += e
        tot_a += ka
        pr("   %4.2f-%-5s | %2d of %-3d      | %3d of %-3d (%3.0f%%)          | %5.1f | %+5.1f" % (
            lo, ("%.2f" % hi) if hi < 99 else "up", ka, len(aa), kb, len(bb), 100 * rate, e, e - ka))
    pr("   total: meow %d, at the top three's band rates %.1f, gap %+.1f wins" % (tot_a, tot_e, tot_e - tot_a))


for key, rnd in (("P", 300), ("total", 300), ("P", 350), ("total", 400), ("P", 400)):
    table("all maps", me, top, rnd, key)
table("small maps", [r for r in me if small(r)], [r for r in top if small(r)], 300, "P")
table("big maps", [r for r in me if big(r)], [r for r in top if big(r)], 300, "P")
table("live bot, all maps", [r for r in me if r["build"] == "live"], top, 300, "P")

pr("\n== 2. Pooled fit over meow's and the top three's races: win ~ c + b*ln(ratio) + m*[meow] + s*[meow]*ln(ratio)")
for key, rnd in (("P", 300), ("total", 300), ("P", 350), ("total", 400), ("P", 400)):
    for label, extra in (("edge only", False), ("edge and slope", True)):
        X, y = [], []
        for grp, flag in ((me, 1.0), (top, 0.0)):
            for r in grp:
                v = R.ratio(r, rnd, key)
                if v is None or v <= 0:
                    continue
                lv = math.log(v)
                row = [1.0, lv, flag]
                if extra:
                    row.append(flag * lv)
                X.append(row)
                y.append(1 if r["won"] else 0)
        beta, cov, ll = Y.logit_fit(X, y, ridge=1e-4)
        se = [math.sqrt(max(0.0, cov[i][i])) for i in range(len(beta))]
        s = "   %s@%d %-14s c=%+.2f b=%.2f  meow edge m=%+.2f (se %.2f; 80%% range %+.2f to %+.2f)" % (
            key, rnd, label, beta[0], beta[1], beta[2], se[2], beta[2] - 1.2816 * se[2], beta[2] + 1.2816 * se[2])
        if extra:
            s += "  slope term s=%+.2f (se %.2f)" % (beta[3], se[3])
        pr(s)

pr("\n== 3. Medians per race: final longest / potential at round 300 (theirs: live small 0.65, test 0.79, opponents 0.75, forgot 0.85, SSS 0.73, Vibing++ 0.71; big 0.42 / 0.36 / 0.38 / 0.53 / 0.46 / 0.46)")
for gname, grp in (("meow live", [r for r in me if r["build"] == "live"]), ("meow test", [r for r in me if r["build"] == "test"]),
                   ("opponents", opp), ("forgot", [r for r in top if r["group"] == "forgot"]),
                   ("SSS", [r for r in top if r["group"] == "SSS"]), ("Vibing++", [r for r in top if r["group"] == "Vibing++"])):
    for cls, lab in ((small, "small"), (big, "big")):
        rs = [r for r in grp if cls(r)]
        v = [R.snap(r, "end", "L") / R.snap(r, 300, "P") for r in rs if R.snap(r, 300, "P")]
        c = [R.snap(r, "end", "L") / R.snap(r, "end", "P") for r in rs if R.snap(r, "end", "P")]
        v4 = [R.snap(r, "end", "L") / R.snap(r, 400, "P") for r in rs if R.snap(r, 400, "P")]
        pr("   %-10s %-5s n=%3d  final longest / P at 300: median %.2f mean %.2f | / P at 400: median %.2f | completeness at the end: median %.2f" % (
            gname, lab, len(rs), Y.med(v), Y.mean(v), Y.med(v4), Y.med(c)))

pr("\n== 4. Who has started to convert by round 400: longest / potential at round 400 (median), and wins by it")
for gname, grp in (("meow", me), ("opponents", opp), ("top three", top)):
    for cls, lab in ((small, "small"), (big, "big")):
        rs = [r for r in grp if cls(r)]
        c4 = [R.snap(r, 400, "L") / R.snap(r, 400, "P") for r in rs if R.snap(r, 400, "P")]
        c35 = [R.snap(r, 350, "L") / R.snap(r, 350, "P") for r in rs if R.snap(r, 350, "P")]
        c45 = [R.snap(r, 450, "L") / R.snap(r, 450, "P") for r in rs if R.snap(r, 450, "P")]
        pr("   %-10s %-5s longest / potential at 350 %.2f, at 400 %.2f, at 450 %.2f" % (gname, lab, Y.med(c35), Y.med(c4), Y.med(c45)))

pr("\n== 5. Our races that start level or better (P ratio at 300 of 0.8+): by map and opponent")
lev = [r for r in me if R.ratio(r, 300, "P") is not None and R.ratio(r, 300, "P") >= 0.8]
from collections import Counter
cm = Counter()
for r in lev:
    cm[(r["map"], r["oname"][:14], r["won"])] += 1
for k, v in sorted(cm.items()):
    pr("   ", k, v)
pr("   total", len(lev), "won", sum(r["won"] for r in lev))
OUTF.close()
