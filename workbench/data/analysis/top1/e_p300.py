#!/usr/bin/env python3
"""Win rate in round-500 games with both queens dead by own / enemy potential at round 300 (before most feeding) and at
round 350, per group and map class; and how the potential moves from 300 to 400 to the end on each side.
Potential P = longest + pearls all other own dragons would drop. Reads e_out/w4. Output: e_out/p300.txt"""
from collections import defaultdict

import e_data as D

P = D.Out("p300.txt")
BANDS = ((0, 0.5), (0.5, 0.8), (0.8, 1.0), (1.0, 1.25), (1.25, 99))


def pot(r, rnd, own=True):
    t = r.tl(rnd, own)
    return t[3] + t[12]


def lend(r, own=True):
    f = (r.s if own else r.o)["final"]
    return f["top"][0][0] if f["top"] else 0


def pend(r, own=True):
    return lend(r, own) + (r.s if own else r.o)["final"]["pot"]


def main():
    recs = [r for r in D.rows() if r.bd]
    by = defaultdict(list)
    for r in recs:
        for g in D.groups(r):
            by[g].append(r)
    for rnd in (300, 350, 400):
        for cls, cname in ((None, "all maps"), (False, "maps of 1,200 cells or fewer"), (True, "maps over 1,200 cells")):
            P("\n== won / games by own P / enemy P at round %d, %s:  under 0.5 | 0.5-0.8 | 0.8-1.0 | 1.0-1.25 | over 1.25 || 0.8-1.25 together" % (rnd, cname))
            for g in ("meow live", "meow test", "meow", "opp", "test4 (vs us)", "WHQ (vs us)", "forgot", "SSS", "Vibing++", "top3", "top3 vs t4/WHQ"):
                v = [r for r in by.get(g, []) if cls is None or r.big == cls]
                if not v:
                    continue
                cells = []
                for lo, hi in BANDS:
                    w = [r for r in v if lo <= pot(r, rnd) / max(1, pot(r, rnd, False)) < hi]
                    cells.append("%d of %d" % (sum(r.won for r in w), len(w)))
                lv = [r for r in v if 0.8 <= pot(r, rnd) / max(1, pot(r, rnd, False)) < 1.25]
                P("   %-16s %s || %s" % (g, " | ".join("%-10s" % c for c in cells), D.frac(sum(r.won for r in lv), len(lv))))
    P("\n== how the potential moves (medians): own P at 300 -> 350 -> 400 -> 450 -> end, and the change 300 -> end as a share")
    for cls, cname in ((False, "maps of 1,200 cells or fewer"), (True, "maps over 1,200 cells")):
        P("   %s" % cname)
        for g in ("meow live", "meow test", "opp", "test4 (vs us)", "WHQ (vs us)", "forgot", "SSS", "Vibing++"):
            v = [r for r in by.get(g, []) if r.big == cls]
            if not v:
                continue
            P("      %-16s %s -> %s -> %s -> %s -> %s | P(end) / P(300): median %s | P(400) / P(300): %s | P(end) / P(400): %s" % (
                g, D.med([pot(r, 300) for r in v]), D.med([pot(r, 350) for r in v]), D.med([pot(r, 400) for r in v]), D.med([pot(r, 450) for r in v]),
                D.med([pend(r) for r in v]), D.med([pend(r) / max(1, pot(r, 300)) for r in v], 2), D.med([pot(r, 400) / max(1, pot(r, 300)) for r in v], 2),
                D.med([pend(r) / max(1, pot(r, 400)) for r in v], 2)))
    P("\n== final longest as a share of the potential at round 300 (what the team had before feeding), medians")
    for cls, cname in ((False, "maps of 1,200 cells or fewer"), (True, "maps over 1,200 cells")):
        P("   %s" % cname)
        for g in ("meow live", "meow test", "opp", "test4 (vs us)", "WHQ (vs us)", "forgot", "SSS", "Vibing++"):
            v = [r for r in by.get(g, []) if r.big == cls and pot(r, 300) >= 20]
            if not v:
                continue
            P("      %-16s final longest / P(300): %s | / P(350): %s | / P(400): %s   (%d games with P(300) of 20+)" % (
                g, D.med([lend(r) / pot(r, 300) for r in v], 2), D.med([lend(r) / max(1, pot(r, 350)) for r in v], 2),
                D.med([lend(r) / max(1, pot(r, 400)) for r in v], 2), len(v)))


if __name__ == "__main__":
    main()
