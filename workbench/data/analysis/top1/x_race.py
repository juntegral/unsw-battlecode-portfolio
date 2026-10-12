#!/usr/bin/env python3
"""The longest-dragon race (an item B did not propose): round-500 games with both queens dead.
By total-length ratio at round 400: games, wins, the longest dragon of both sides at rounds 300, 400 and the end.
And: losses in which we had MORE total length than the enemy at round 400 (lost on consolidation alone).
Own code on x_out/c1/. Output: x_out/race.txt"""
from collections import Counter, defaultdict
import x_load as X
out = open("x_out/race.txt", "w")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.write(s + "\n")
gs = [g for g in X.games("c1") if g["d"] and X.is_csv(g)]
def med(v):
    v = sorted(v); return v[len(v) // 2] if v else 0
BANDS = ((0, 0.5, "under 0.5"), (0.5, 0.8, "0.5-0.8"), (0.8, 1.0, "0.8-1"), (1.0, 1.25, "1-1.25"), (1.25, 2.0, "1.25-2"), (2.0, 99, "over 2"))
for name, pred in (("meow all", lambda g, s: g[s] == X.ME), ("meow live", lambda g, s: g[s] == X.ME and X.build(g) == "live"),
                   ("top three", lambda g, s: g[s] in X.TOP3), ("our opponents", lambda g, s: g[X.other(s)] == X.ME)):
    P("\n== %s: round-500 games with both queens dead, by own / enemy total length at round 400" % name)
    rows = defaultdict(list)
    n_all = 0
    for g in gs:
        for side in "AB":
            if not X.in_study(g, side) or not pred(g, side):
                continue
            n_all += 1
            d = g["d"]; es = X.other(side); e = d["end"]
            if e["rounds"] < 500 or e["qalive"][side] or e["qalive"][es]:
                continue
            o4, e4 = X.stats_at(d, 400, side), X.stats_at(d, 400, es)
            o3, e3 = X.stats_at(d, 300, side), X.stats_at(d, 300, es)
            if not o4 or not e4 or not e4[1]:
                continue
            ratio = o4[1] / e4[1]
            rows[next(b[2] for b in BANDS if b[0] <= ratio < b[1])].append(dict(
                win=X.won(g, side), ol3=o3[2], el3=e3[2], ol4=o4[2], el4=e4[2], ole=e["st"][side][2], ele=e["st"][es][2],
                ot4=o4[1], et4=e4[1], ou4=o4[0], eu4=e4[0], gid=g["gid"], map=g["map"], cells=g["cells"],
                ote=e["st"][side][1], ete=e["st"][es][1]))
    P("   %-10s %-18s %-26s %-26s %-26s %-22s" % ("ratio", "won", "longest r300 own:enemy", "longest r400 own:enemy", "longest end own:enemy", "units r400 own:enemy"))
    tot = Counter()
    for lo, hi, lab in BANDS:
        v = rows[lab]
        if not v:
            continue
        w = sum(x["win"] for x in v)
        P("   %-10s %-18s %-26s %-26s %-26s %-22s" % (lab, X.frac(w, len(v)), "%d : %d" % (med([x["ol3"] for x in v]), med([x["el3"] for x in v])),
          "%d : %d" % (med([x["ol4"] for x in v]), med([x["el4"] for x in v])), "%d : %d" % (med([x["ole"] for x in v]), med([x["ele"] for x in v])),
          "%d : %d" % (med([x["ou4"] for x in v]), med([x["eu4"] for x in v]))))
        tot["n"] += len(v); tot["w"] += w
        if lo >= 1.0:
            tot["ahead_n"] += len(v); tot["ahead_w"] += w
        if lo >= 0.8:
            tot["near_n"] += len(v); tot["near_w"] += w
    P("   all: %s of this group's %d games are such games; with total length at least level at round 400: %s; at least 0.8: %s" % (
        X.frac(tot["w"], tot["n"]), n_all, X.frac(tot["ahead_w"], tot["ahead_n"]), X.frac(tot["near_w"], tot["near_n"])))
    if name.startswith("meow all"):
        P("   our losses with total length at least level at round 400 (lost on the longest dragon alone):")
        for lab in ("1-1.25", "1.25-2", "over 2"):
            for x in rows[lab]:
                if not x["win"]:
                    P("      game %d %-16s total r400 %d vs %d, longest r300 %d vs %d, r400 %d vs %d, end %d vs %d; total at end %d vs %d" % (
                        x["gid"], x["map"], x["ot4"], x["et4"], x["ol3"], x["el3"], x["ol4"], x["el4"], x["ole"], x["ele"], x["ote"], x["ete"]))
