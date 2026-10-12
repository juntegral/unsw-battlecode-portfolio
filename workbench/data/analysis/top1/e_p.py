#!/usr/bin/env python3
"""The race as "potential x completeness". Round-500 games with both queens dead.

potential P(r)  = the longest dragon + the pearls every other own dragon would drop if it died now (sum of ceil(L/2)).
                  It is what the longest dragon would be if the whole team were fed to it without loss. Feeding does
                  not change P (a 2-long feeder is worth 1 before and after); eating a natural pearl adds 1 when the
                  leader eats it and about 0.5 when a small dragon does; a lost pearl or a rammed dragon lowers it.
completeness c  = longest / P: how much of the potential is already inside the longest dragon.
The final longest dragon = P(end) x c(end).

Per group and map class: medians of P and c at rounds 300 / 350 / 400 / 450 / the end, own and enemy; own P as a share
of the enemy's P; who was ahead on P at round 400 and at the end and who won; and what-ifs on played games:
  A  our final longest replaced by c_ref x our own final P (c_ref = 0.75, 0.85, 0.95), the enemy unchanged;
  B  both sides at full completeness (the winner is whoever has more final P);
  C  the same c for both sides (ours raised or lowered to the enemy's c in that game).
Reads e_out/w4. Output: e_out/p_potential.txt and e_out/p_games.txt (one line per game of ours)
"""
from collections import defaultdict

import e_data as D
import e_lib as E

P = D.Out("p_potential.txt")
RS = (300, 350, 400, 450)


def pot(r, rnd, own=True):
    t = r.tl(rnd, own)
    return t[3] + t[12]


def pend(r, own=True):
    f = (r.s if own else r.o)["final"]
    return (f["top"][0][0] if f["top"] else 0) + f["pot"]


def lend(r, own=True):
    f = (r.s if own else r.o)["final"]
    return f["top"][0][0] if f["top"] else 0


def block(recs, title):
    n = len(recs)
    if not n:
        return
    P("\n--- %s: %d games, won %s" % (title, n, D.frac(sum(r.won for r in recs), n)))
    P("    %-44s %7s %7s %7s %7s %7s" % ("median at round", 300, 350, 400, 450, "end"))
    P("    %-44s" % "own potential P" + "".join("%8s" % D.med([pot(r, x) for r in recs]) for x in RS) + "%8s" % D.med([pend(r) for r in recs]))
    P("    %-44s" % "enemy's potential P" + "".join("%8s" % D.med([pot(r, x, False) for r in recs]) for x in RS) + "%8s" % D.med([pend(r, False) for r in recs]))
    P("    %-44s" % "own P / enemy's P" + "".join("%8s" % D.med([pot(r, x) / max(1, pot(r, x, False)) for r in recs], 2) for x in RS)
      + "%8s" % D.med([pend(r) / max(1, pend(r, False)) for r in recs], 2))
    P("    %-44s" % "own completeness c = longest / P" + "".join("%8s" % D.med([r.tl(x)[3] / max(1, pot(r, x)) for r in recs], 2) for x in RS)
      + "%8s" % D.med([lend(r) / max(1, pend(r)) for r in recs], 2))
    P("    %-44s" % "enemy's completeness" + "".join("%8s" % D.med([r.tl(x, False)[3] / max(1, pot(r, x, False)) for r in recs], 2) for x in RS)
      + "%8s" % D.med([lend(r, False) / max(1, pend(r, False)) for r in recs], 2))
    P("    %-44s" % "own units" + "".join("%8s" % D.med([r.tl(x)[1] for r in recs]) for x in RS) + "%8s" % D.med([r.s["final"]["units"] for r in recs]))
    P("    %-44s" % "enemy's units" + "".join("%8s" % D.med([r.tl(x, False)[1] for r in recs]) for x in RS) + "%8s" % D.med([r.o["final"]["units"] for r in recs]))
    P("    own P gained from round 400 to the end: median %s (enemy's %s); from 300 to 400: %s (enemy's %s)" % (
        D.med([pend(r) - pot(r, 400) for r in recs]), D.med([pend(r, False) - pot(r, 400, False) for r in recs]),
        D.med([pot(r, 400) - pot(r, 300) for r in recs]), D.med([pot(r, 400, False) - pot(r, 300, False) for r in recs])))
    for lab, fn in (("round 300", lambda r: pot(r, 300) >= pot(r, 300, False)), ("round 400", lambda r: pot(r, 400) >= pot(r, 400, False)),
                    ("the end", lambda r: pend(r) >= pend(r, False))):
        a = [r for r in recs if fn(r)]
        b = [r for r in recs if not fn(r)]
        P("    own P at least the enemy's at %-10s %3d games, won %-16s | below: %3d games, won %s" % (
            lab + ":", len(a), D.frac(sum(r.won for r in a), len(a)), len(b), D.frac(sum(r.won for r in b), len(b))))
    for lo, hi in ((0, 0.5), (0.5, 0.8), (0.8, 1.0), (1.0, 1.25), (1.25, 99)):
        v = [r for r in recs if lo <= pot(r, 400) / max(1, pot(r, 400, False)) < hi]
        if v:
            P("      own P / enemy's P at round 400 in [%.2f, %.2f): %3d games, won %-14s | own c at the end %s, enemy's %s | own final longest %s, enemy's %s" % (
                lo, hi, len(v), D.frac(sum(r.won for r in v), len(v)), D.med([lend(r) / max(1, pend(r)) for r in v], 2),
                D.med([lend(r, False) / max(1, pend(r, False)) for r in v], 2), D.med([lend(r) for r in v]), D.med([lend(r, False) for r in v])))
    lost = [r for r in recs if not r.won]
    won = [r for r in recs if r.won]
    for c in (0.75, 0.85, 0.95):
        fl = [r for r in lost if c * pend(r) > lend(r, False)]
        P("    what-if A: our final longest = %.2f x our final P, enemy unchanged: %d of the %d losses turn" % (c, len(fl), len(lost)))
    fb = [r for r in lost if pend(r) > pend(r, False)]
    wb = [r for r in won if pend(r) < pend(r, False)]
    P("    what-if B: both sides complete (more final P wins): %d of %d losses turn into wins, %d of %d wins into losses (net %+d)" % (
        len(fb), len(lost), len(wb), len(won), len(fb) - len(wb)))
    fc = [r for r in lost if pend(r) * (lend(r, False) / max(1, pend(r, False))) > lend(r, False)]
    wc = [r for r in won if lend(r) / max(1, pend(r)) > lend(r, False) / max(1, pend(r, False)) and pend(r) * (lend(r, False) / max(1, pend(r, False))) < lend(r, False)]
    P("    what-if C: our c set to the enemy's c of that game: %d of %d losses turn; %d of %d wins would be lost (wins we owe to a better c)" % (
        len(fc), len(lost), len(wc), len(won)))
    return


def main():
    recs = D.rows()
    by = defaultdict(list)
    for r in recs:
        for g in D.groups(r):
            by[g].append(r)
    order = list(D.ORDER) + ["top3 vs t4/WHQ", "test4 (vs us)", "WHQ (vs us)", "test4 (vs top3)", "WHQ (vs top3)"]
    for cls, name in ((None, "ALL MAPS"), (False, "MAPS OF 1,200 CELLS OR FEWER"), (True, "MAPS OVER 1,200 CELLS")):
        P("\n\n==================== %s: round-500 games with both queens dead ====================" % name)
        for g in order:
            v = [r for r in by.get(g, []) if r.bd and (cls is None or r.big == cls)]
            block(v, g)
    # one line per game of ours
    G = D.Out("p_games.txt")
    G.f.write("gid | map | cells | run | opponent | result | P own:enemy at 300, 350, 400, 450, end | longest own:enemy at 400, end | c own:enemy at the end | units at the end\n")
    for r in sorted(by.get("meow", []), key=lambda x: (x.map, x.gid)):
        if not r.bd:
            continue
        G.f.write("%d | %s | %d | %s | %s | %s | %s | %d:%d, %d:%d | %.2f:%.2f | %d:%d\n" % (
            r.gid, r.map, r.cells, r.set, E.NAMES.get(r.opp, str(r.opp)), "W" if r.won else "L",
            ", ".join("%d:%d" % (pot(r, x), pot(r, x, False)) for x in RS) + ", %d:%d" % (pend(r), pend(r, False)),
            r.tl(400)[3], r.tl(400, False)[3], lend(r), lend(r, False), lend(r) / max(1, pend(r)), lend(r, False) / max(1, pend(r, False)),
            r.s["final"]["units"], r.o["final"]["units"]))


if __name__ == "__main__":
    main()
