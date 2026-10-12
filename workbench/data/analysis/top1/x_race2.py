#!/usr/bin/env python3
"""The longest-dragon race by map class (our leader rules start at round 150 on maps over 1,200 cells, at 300 on
the others). Round-500 games with both queens dead: win rate by own / enemy total length at round 400, and the
longest dragon of both sides at rounds 150, 300, 400 and the end. Own code on x_out/c1/. Output: x_out/race2.txt"""
from collections import Counter, defaultdict
import x_load as X
out = open("x_out/race2.txt", "w")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.write(s + "\n")
gs = [g for g in X.games("c1") if g["d"] and X.is_csv(g)]
def med(v):
    v = sorted(v); return v[len(v) // 2] if v else 0
BANDS = ((0, 0.5, "under 0.5"), (0.5, 0.8, "0.5-0.8"), (0.8, 1.25, "0.8-1.25"), (1.25, 99, "over 1.25"))
for cname, cpred in (("maps over 1,200 cells", lambda g: g["cells"] > 1200), ("maps of 1,200 cells or fewer", lambda g: g["cells"] <= 1200)):
    for name, pred in (("meow all", lambda g, s: g[s] == X.ME), ("meow live", lambda g, s: g[s] == X.ME and X.build(g) == "live"),
                       ("top three", lambda g, s: g[s] in X.TOP3), ("top three vs test4/WHQ", lambda g, s: g[s] in X.TOP3 and X.opp(g, s)[0] in (X.T4, X.WHQ)),
                       ("our opponents", lambda g, s: g[X.other(s)] == X.ME)):
        rows = defaultdict(list)
        n_all = n_dd = w_dd = 0
        allr = []
        for g in gs:
            if not cpred(g):
                continue
            for side in "AB":
                if not X.in_study(g, side) or not pred(g, side):
                    continue
                n_all += 1
                d = g["d"]; es = X.other(side); e = d["end"]
                if e["rounds"] < 500 or e["qalive"][side] or e["qalive"][es]:
                    continue
                n_dd += 1; w_dd += X.won(g, side)
                st = {R: (X.stats_at(d, R, side), X.stats_at(d, R, es)) for R in (150, 300, 400)}
                if not st[400][0] or not st[400][1] or not st[400][1][1]:
                    continue
                ratio = st[400][0][1] / st[400][1][1]
                rec = dict(win=X.won(g, side), ole=e["st"][side][2], ele=e["st"][es][2])
                for R in (150, 300, 400):
                    rec["ol%d" % R] = st[R][0][2]; rec["el%d" % R] = st[R][1][2]
                    rec["ou%d" % R] = st[R][0][0]; rec["eu%d" % R] = st[R][1][0]
                rows[next(b[2] for b in BANDS if b[0] <= ratio < b[1])].append(rec)
                allr.append(rec)
        P("\n== %s, %s: %d games, %d end at round 500 with both queens dead, won %s" % (cname, name, n_all, n_dd, X.frac(w_dd, n_dd)))
        P("   %-11s %-16s %-22s %-22s %-22s %-22s %-18s" % ("ratio r400", "won", "longest r150 own:enemy", "r300", "r400", "end", "units r400"))
        for lo, hi, lab in BANDS:
            v = rows[lab]
            if not v:
                continue
            w = sum(x["win"] for x in v)
            P("   %-11s %-16s %-22s %-22s %-22s %-22s %-18s" % (lab, X.frac(w, len(v)),
              "%d : %d" % (med([x["ol150"] for x in v]), med([x["el150"] for x in v])),
              "%d : %d" % (med([x["ol300"] for x in v]), med([x["el300"] for x in v])),
              "%d : %d" % (med([x["ol400"] for x in v]), med([x["el400"] for x in v])),
              "%d : %d" % (med([x["ole"] for x in v]), med([x["ele"] for x in v])),
              "%d : %d" % (med([x["ou400"] for x in v]), med([x["eu400"] for x in v]))))
# our wins on big maps one by one
P("\n== Our wins on maps over 1,200 cells, one by one (all are round-500 games)")
for g in gs:
    side = X.side_of(g, X.ME)
    if side is None or not X.in_study(g, side) or g["cells"] <= 1200 or not X.won(g, side):
        continue
    d = g["d"]; es = X.other(side); e = d["end"]
    s = {R: (X.stats_at(d, R, side), X.stats_at(d, R, es)) for R in (150, 300, 400)}
    P("   game %d %-15s %-14s %-18s | longest own:enemy r150 %d:%d r300 %d:%d r400 %d:%d end %d:%d | total r300 %d:%d r400 %d:%d | queens alive own/her: %s/%s" % (
        g["gid"], g["map"], X.opp(g, side)[1][:14], g["set"], s[150][0][2], s[150][1][2], s[300][0][2], s[300][1][2], s[400][0][2], s[400][1][2],
        e["st"][side][2], e["st"][es][2], s[300][0][1], s[300][1][1], s[400][0][1], s[400][1][1], e["qalive"][side], e["qalive"][es]))
