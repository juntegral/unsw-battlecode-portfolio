#!/usr/bin/env python3
"""Spread of the final completeness c = final longest / final potential over all sides of round-500 games with both
queens dead, by map class and team; and the win rate by c band inside a band of potential.
Reads e_out/w4. Output: e_out/cdist.txt"""
from collections import defaultdict

import e_data as D
import e_lib as E

P = D.Out("cdist.txt")


def lend(r, own=True):
    f = (r.s if own else r.o)["final"]
    return f["top"][0][0] if f["top"] else 0


def pend(r, own=True):
    f = (r.s if own else r.o)["final"]
    return lend(r, own) + f["pot"]


def pot(r, rnd, own=True):
    t = r.tl(rnd, own)
    return t[3] + t[12]


def q(v):
    v = sorted(v)
    n = len(v)
    return "n %4d | 10%% %.2f | 25%% %.2f | median %.2f | 75%% %.2f | 90%% %.2f | share at 0.75+: %s | at 0.9+: %s" % (
        n, v[n // 10], v[n // 4], v[n // 2], v[(3 * n) // 4], v[(9 * n) // 10], D.pct(sum(1 for x in v if x >= 0.75), n), D.pct(sum(1 for x in v if x >= 0.9), n))


def main():
    recs = [r for r in D.rows() if r.bd]
    by = defaultdict(list)
    for r in recs:
        for g in D.groups(r):
            by[g].append(r)
    for cls, cname in ((False, "maps of 1,200 cells or fewer"), (True, "maps over 1,200 cells")):
        P("\n== %s: final completeness, sides with a final potential of 20 or more" % cname)
        for g in ("meow live", "meow test", "meow", "opp", "test4 (vs us)", "WHQ (vs us)", "forgot", "SSS", "Vibing++", "top3"):
            v = [lend(r) / pend(r) for r in by.get(g, []) if r.big == cls and pend(r) >= 20]
            if len(v) >= 5:
                P("   %-16s %s" % (g, q(v)))
        P("   by the side's units at round 400 (all sides of all walked games on these maps):")
        allr = [r for r in recs if r.big == cls and pend(r) >= 20]
        for lo, hi in ((0, 9), (10, 19), (20, 29), (30, 44), (45, 64)):
            v = [lend(r) / pend(r) for r in allr if lo <= r.tl(400)[1] <= hi]
            if len(v) >= 5:
                P("      units %2d-%2d: %s" % (lo, hi, q(v)))
        P("   by map (all sides):")
        maps = sorted(set(r.map for r in allr))
        for m in maps:
            v = [lend(r) / pend(r) for r in allr if r.map == m]
            if len(v) >= 5:
                P("      %-18s %s" % (m, q(v)))
    P("\n== win rate by own completeness at the end, inside bands of own P / enemy P at round 400 (all sides of all walked games)")
    for lo, hi in ((0.5, 0.8), (0.8, 1.0), (1.0, 1.25), (1.25, 2.0)):
        line = "   P ratio [%.2f, %.2f):" % (lo, hi)
        v = [r for r in recs if lo <= pot(r, 400) / max(1, pot(r, 400, False)) < hi]
        for a, b in ((0, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.01)):
            w = [r for r in v if a <= lend(r) / max(1, pend(r)) < b]
            line += "  c %.1f-%.1f: %s" % (a, b, D.frac(sum(r.won for r in w), len(w)))
        P(line)
    P("\n== our games: own completeness against the enemy's in the same game")
    for g in ("meow",):
        for cls, cname in ((False, "small maps"), (True, "big maps")):
            v = [r for r in by[g] if r.big == cls and pend(r) >= 20 and pend(r, False) >= 20]
            hi = [r for r in v if lend(r) / pend(r) > lend(r, False) / pend(r, False)]
            P("   %s: %d games with both potentials 20+; our c is the higher one in %d (won %d of those), the lower one in %d (won %d)" % (
                cname, len(v), len(hi), sum(r.won for r in hi), len(v) - len(hi), sum(r.won for r in v if r not in hi)))


if __name__ == "__main__":
    main()
