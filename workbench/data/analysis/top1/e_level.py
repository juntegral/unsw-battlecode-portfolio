#!/usr/bin/env python3
"""Level races against the same two opponents. Round-500 games with both queens dead against test4 and WeHaveQuizzes
only: won / games by own P / enemy P (potential) at rounds 300, 350 and 400, for meow (live bot, test builds) and for
each top team; and the list of our games in the level band (0.8-1.25 at round 350) with how they went.
Also: the red team's band (own / enemy TOTAL length at round 400 in 0.8-1.25, maps of 1,200 cells or fewer) with the
same games' totals and potentials at round 300.  Reads e_out/w4. Output: e_out/level.txt"""
from collections import defaultdict

import e_data as D
import e_lib as E

P = D.Out("level.txt")
BANDS = ((0, 0.5), (0.5, 0.8), (0.8, 1.25), (1.25, 99))


def pot(r, rnd, own=True):
    t = r.tl(rnd, own)
    return t[3] + t[12]


def lend(r, own=True):
    f = (r.s if own else r.o)["final"]
    return f["top"][0][0] if f["top"] else 0


def pend(r, own=True):
    return lend(r, own) + (r.s if own else r.o)["final"]["pot"]


def main():
    recs = [r for r in D.rows() if r.bd and r.study]
    groups = (("meow live", lambda r: r.team == E.ME and r.build == "live"), ("meow test builds", lambda r: r.team == E.ME and r.build != "live"),
              ("meow all", lambda r: r.team == E.ME), ("forgot", lambda r: r.team == E.FORGOT), ("SSS", lambda r: r.team == E.SSS),
              ("Vibing++", lambda r: r.team == E.VIB), ("top three", lambda r: r.team in E.TOP3))
    for opp_name, osel in (("test4 and WeHaveQuizzes", lambda r: r.opp in (E.T4, E.WHQ)), ("test4", lambda r: r.opp == E.T4), ("WeHaveQuizzes", lambda r: r.opp == E.WHQ),
                           ("any 2000+ opponent", lambda r: True)):
        for rnd in (300, 350, 400):
            P("\n== against %s: won / games by own P / enemy P at round %d: under 0.5 | 0.5-0.8 | 0.8-1.25 | over 1.25" % (opp_name, rnd))
            for g, sel in groups:
                v = [r for r in recs if sel(r) and osel(r)]
                if not v:
                    continue
                cells = []
                for lo, hi in BANDS:
                    w = [r for r in v if lo <= pot(r, rnd) / max(1, pot(r, rnd, False)) < hi]
                    cells.append("%d of %d" % (sum(r.won for r in w), len(w)))
                P("   %-18s %s" % (g, " | ".join("%-9s" % c for c in cells)))
    P("\n== our games with own P / enemy P between 0.8 and 1.25 at round 350 (24 games): game, map, run, opponent, result, P own:enemy at 300 / 350 / 400 / end, "
      "final longest own:enemy, c own:enemy, leader cuts from 395")
    v = [r for r in recs if r.team == E.ME and 0.8 <= pot(r, 350) / max(1, pot(r, 350, False)) < 1.25]
    for r in sorted(v, key=lambda x: (x.won, x.map, x.gid)):
        cuts = sum(1 for x in r.s["splits"] if x[7] and x[3] >= 8 and x[4] <= 3 and x[0] >= 395)
        P("   %d | %s | %s | %s | %s | %d:%d / %d:%d / %d:%d / %d:%d | %d:%d | %.2f:%.2f | %d" % (
            r.gid, r.map, r.set, E.NAMES.get(r.opp, str(r.opp)), "W" if r.won else "L", pot(r, 300), pot(r, 300, False), pot(r, 350), pot(r, 350, False),
            pot(r, 400), pot(r, 400, False), pend(r), pend(r, False), lend(r), lend(r, False), lend(r) / max(1, pend(r)), lend(r, False) / max(1, pend(r, False)), cuts))
    P("\n== the red team's band: maps of 1,200 cells or fewer, own / enemy TOTAL length at round 400 between 0.8 and 1.25")
    for g, sel in (("meow all", lambda r: r.team == E.ME), ("top three", lambda r: r.team in E.TOP3)):
        v = [r for r in recs if sel(r) and not r.big and r.ratio(400) is not None and 0.8 <= r.ratio(400) <= 1.25]
        P("   %-10s %d games, won %d | total at round 300 own : enemy (medians) %s : %s | at 350 %s : %s | at 400 %s : %s | P at 300 %s : %s | P at 400 %s : %s | "
          "games in which the enemy's total at round 300 was more than 1.25 times ours: %d (won %d)" % (
              g, len(v), sum(r.won for r in v), D.med([r.tl(300)[2] for r in v]), D.med([r.tl(300, False)[2] for r in v]),
              D.med([r.tl(350)[2] for r in v]), D.med([r.tl(350, False)[2] for r in v]), D.med([r.tl(400)[2] for r in v]), D.med([r.tl(400, False)[2] for r in v]),
              D.med([pot(r, 300) for r in v]), D.med([pot(r, 300, False) for r in v]), D.med([pot(r, 400) for r in v]), D.med([pot(r, 400, False) for r in v]),
              sum(1 for r in v if r.tl(300, False)[2] > 1.25 * r.tl(300)[2]), sum(1 for r in v if r.tl(300, False)[2] > 1.25 * r.tl(300)[2] and r.won)))
        lv = [r for r in v if r.tl(300, False)[2] <= 1.25 * r.tl(300)[2]]
        P("              the others (enemy's total at round 300 at most 1.25 times ours): %d games, won %d" % (len(lv), sum(r.won for r in lv)))


if __name__ == "__main__":
    main()
