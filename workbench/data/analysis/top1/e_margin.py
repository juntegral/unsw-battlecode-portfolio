#!/usr/bin/env python3
"""Margins of our round-500 games with both queens dead: how many losses turn if our final longest dragon were k
segments longer (strict reading: nothing else changes), for all games / the live bot / by opponent / by map class;
and the same if the leader's growth after round 400 were multiplied by a factor (growth = final longest - longest at
round 400, floor 0). Reads e_out/w4. Output: e_out/margin.txt"""
from collections import defaultdict

import e_data as D
import e_lib as E

P = D.Out("margin.txt")


def lend(r, own=True):
    f = (r.s if own else r.o)["final"]
    return f["top"][0][0] if f["top"] else 0


def tot(r, own=True):
    return (r.s if own else r.o)["final"]["total"]


def wins_with(r, mine):
    """Longest rule with the tie-break on total length (our total unchanged)."""
    e = lend(r, False)
    if mine != e:
        return mine > e
    return tot(r) > tot(r, False)


def table(name, recs):
    lost = [r for r in recs if not r.won]
    P("\n--- %s: %d games, won %d, lost %d" % (name, len(recs), len(recs) - len(lost), len(lost)))
    line = "    losses that turn if our final longest were longer by"
    for k in (2, 5, 10, 15, 20, 30):
        line += " | +%d: %d" % (k, sum(1 for r in lost if wins_with(r, lend(r) + k)))
    P(line)
    line = "    losses that turn if our leader's growth after round 400 were multiplied by"
    for f in (1.25, 1.5, 2.0, 3.0):
        n = 0
        for r in lost:
            g = max(0, lend(r) - r.tl(400)[3])
            n += wins_with(r, lend(r) + int(round((f - 1) * g)))
        line += " | x%.2f: %d" % (f, n)
    P(line)
    line = "    the same, but our final longest never above 0.9 of our own final potential"
    for f in (1.25, 1.5, 2.0, 3.0):
        n = 0
        for r in lost:
            g = max(0, lend(r) - r.tl(400)[3])
            cap = int(0.9 * (lend(r) + r.s["final"]["pot"]))
            n += wins_with(r, max(lend(r), min(cap, lend(r) + int(round((f - 1) * g)))))
        line += " | x%.2f: %d" % (f, n)
    P(line)
    line = "    ... and counted only where a leader cut happened from round 395 on (the games the rule can touch)"
    for f in (1.25, 1.5, 2.0, 3.0):
        n = 0
        for r in lost:
            if not any(x[7] and x[3] >= 8 and x[4] <= 3 and x[0] >= 395 for x in r.s["splits"]):
                continue
            g = max(0, lend(r) - r.tl(400)[3])
            cap = int(0.9 * (lend(r) + r.s["final"]["pot"]))
            n += wins_with(r, max(lend(r), min(cap, lend(r) + int(round((f - 1) * g)))))
        line += " | x%.2f: %d" % (f, n)
    P(line)
    P("    median margin of the losses: %s segments; of the wins: %s; losses by 5 or fewer: %d, by 6-10: %d, by 11-20: %d, by more: %d" % (
        D.med([lend(r, False) - lend(r) for r in lost]), D.med([lend(r) - lend(r, False) for r in recs if r.won]),
        sum(1 for r in lost if lend(r, False) - lend(r) <= 5), sum(1 for r in lost if 5 < lend(r, False) - lend(r) <= 10),
        sum(1 for r in lost if 10 < lend(r, False) - lend(r) <= 20), sum(1 for r in lost if lend(r, False) - lend(r) > 20)))


def main():
    recs = [r for r in D.rows() if r.me and r.study and r.bd]
    table("meow, all 401 games: round-500 games with both queens dead", recs)
    table("live bot", [r for r in recs if r.build == "live"])
    table("test builds", [r for r in recs if r.build != "live"])
    table("maps of 1,200 cells or fewer", [r for r in recs if not r.big])
    table("maps over 1,200 cells", [r for r in recs if r.big])
    for t, nm in ((E.T4, "against test4"), (E.WHQ, "against WeHaveQuizzes")):
        table(nm, [r for r in recs if r.opp == t])
    table("against everybody else", [r for r in recs if r.opp not in (E.T4, E.WHQ)])
    P("\nthe losses by 10 or fewer, one per line: game, map, run, opponent, final longest own:enemy, longest at round 400 own:enemy, leader cuts from round 395")
    for r in sorted(recs, key=lambda x: lend(x, False) - lend(x)):
        m = lend(r, False) - lend(r)
        if not r.won and m <= 10:
            cuts = sum(1 for x in r.s["splits"] if x[7] and x[3] >= 8 and x[4] <= 3 and x[0] >= 395)
            P("   %d | %s | %s | %s | %d:%d | %d:%d | %d cuts" % (r.gid, r.map, r.set, E.NAMES.get(r.opp, str(r.opp)), lend(r), lend(r, False),
                                                              r.tl(400)[3], r.tl(400, False)[3], cuts))


if __name__ == "__main__":
    main()
