#!/usr/bin/env python3
"""Question (a): the leader's curve. Round-500 games with both queens dead (the longest dragon decides).

For each group (meow live / meow test builds / meow all / our opponents in the same games / forgot / SSS / Vibing++ /
top three together), by map class (over 1,200 cells / 1,200 or fewer) and by own / enemy total length at round 400:
  games, wins; medians of the longest dragon ("leader of the time") every 25 rounds from 150 to the end, of the lineage
  (the final longest dragon followed back in time), of units and total length, the leader's share of the total; the first
  round the lineage / the leader of the time was 8, 15 and 25 long; the "take-off" (first round from which the team's
  longest dragon grows by 8 or more within 25 rounds) and the growth in the 50 rounds after it.
Reads e_out/w (e_walk.py). Output: e_out/a_curve.txt
"""
import sys

import e_data as D

P = D.Out("a_curve.txt")
RS = list(range(150, 500, 25))


def takeoff(tl, gain=8, span=25, r_from=100):
    """First round r >= r_from (step 5) with longest(r + span) - longest(r) >= gain; and the gain over 50 rounds after."""
    n = len(tl)
    k = span // 5
    for i in range(r_from // 5, n - k):
        if tl[i + k][3] - tl[i][3] >= gain:
            j = min(n - 1, i + 10)
            return tl[i][0], tl[j][3] - tl[i][3], tl[i][3]
    return None, None, None


def table(recs, title):
    if not recs:
        return
    w = sum(r.won for r in recs)
    P("\n--- %s: %d games, won %s" % (title, len(recs), D.frac(w, len(recs))))
    line = "    %-34s" % "round"
    for r in RS:
        line += "%6d" % r
    P(line + "    end")
    for name, fn in (
        ("longest (leader of the time)", lambda x, r: x.tl(r)[3]),
        ("lineage of the final longest", lambda x, r: x.lin_len(r)),
        ("ENEMY's longest", lambda x, r: x.tl(r, False)[3]),
        ("second longest", lambda x, r: x.tl(r)[5]),
        ("units", lambda x, r: x.tl(r)[1]),
        ("total length", lambda x, r: x.tl(r)[2]),
        ("ENEMY's total length", lambda x, r: x.tl(r, False)[2]),
        ("leader's share of total, %", lambda x, r: 100.0 * x.tl(r)[3] / max(1, x.tl(r)[2])),
        ("dragons of 4 or shorter", lambda x, r: x.tl(r)[10]),
        ("dragons of 8+", lambda x, r: x.tl(r)[8]),
    ):
        line = "    %-34s" % name
        for r in RS:
            line += "%6s" % D.med([fn(x, r) for x in recs])
        if name.startswith("longest"):
            line += "%6s" % D.med([x.s["final"]["top"][0][0] for x in recs])
        elif name.startswith("ENEMY's longest"):
            line += "%6s" % D.med([x.o["final"]["top"][0][0] for x in recs])
        elif name.startswith("lineage"):
            line += "%6s" % D.med([x.s["lin"]["len"] for x in recs])
        elif name == "units":
            line += "%6s" % D.med([x.s["final"]["units"] for x in recs])
        elif name == "total length":
            line += "%6s" % D.med([x.s["final"]["total"] for x in recs])
        elif name.startswith("ENEMY's total"):
            line += "%6s" % D.med([x.o["final"]["total"] for x in recs])
        elif name.startswith("leader's share"):
            line += "%6s" % D.med([100.0 * x.s["final"]["top"][0][0] / max(1, x.s["final"]["total"]) for x in recs])
        elif name.startswith("second"):
            line += "%6s" % D.med([(x.s["final"]["top"][1][0] if len(x.s["final"]["top"]) > 1 else 0) for x in recs])
        P(line)
    for T in ("8", "15", "25", "40"):
        a = [x.s["lin"]["first"].get(T) for x in recs]
        b = [x.s["longfirst"].get(T) for x in recs]
        P("    first round at %2s long: lineage median %s (never in %d); leader of the time median %s (never in %d)" % (
            T, D.med(a), sum(v is None for v in a), D.med(b), sum(v is None for v in b)))
    to = [takeoff(x.s["tl"]) for x in recs]
    P("    take-off (longest grows 8+ in 25 rounds): median round %s, never in %d of %d; longest at take-off %s, gain in the 50 rounds after %s" % (
        D.med([t[0] for t in to]), sum(t[0] is None for t in to), len(to), D.med([t[2] for t in to]), D.med([t[1] for t in to])))
    eo = [takeoff(x.o["tl"]) for x in recs]
    P("    the ENEMY's take-off in the same games: median round %s, never in %d; gain in the 50 rounds after %s" % (
        D.med([t[0] for t in eo]), sum(t[0] is None for t in eo), D.med([t[1] for t in eo])))
    hs = [sum(1 for h in x.s["lin"]["hand"] if h[0] >= 300 and h[3] >= 8) for x in recs]
    P("    handovers of the lineage to a split child from round 300 (parent 8+): mean %s per game; games with at least one: %d" % (
        D.mean(hs), sum(1 for h in hs if h)))


def main():
    recs = D.rows()
    by = {}
    for r in recs:
        for g in D.groups(r):
            by.setdefault(g, []).append(r)
    P("Games walked: %d sides. Study sides per group: %s" % (len(recs), {g: len(v) for g, v in by.items()}))
    order = list(D.ORDER) + ["top3 vs t4/WHQ", "test4 (vs us)", "WHQ (vs us)", "test4 (vs top3)", "WHQ (vs top3)"]
    for cls, name in ((False, "MAPS OF 1,200 CELLS OR FEWER"), (True, "MAPS OVER 1,200 CELLS")):
        P("\n\n==================== %s: round-500 games with both queens dead ====================" % name)
        for g in order:
            v = [r for r in by.get(g, []) if r.bd and r.big == cls]
            if not v:
                continue
            P("\n########## %s (%s): %d such games of %d, won %s" % (g, name.lower(), len(v), sum(1 for r in by[g] if r.big == cls),
                                                                  D.frac(sum(r.won for r in v), len(v))))
            for band in D.BANDS:
                table([r for r in v if D.band400(r) == band], "%s | total-length ratio at round 400 %s" % (g, band))
            if "--split" in sys.argv:
                lv = [r for r in v if D.band400(r) == "0.8-1.25"]
                table([r for r in lv if r.won], "%s | level at round 400, WON" % g)
                table([r for r in lv if not r.won], "%s | level at round 400, LOST" % g)


if __name__ == "__main__":
    main()
