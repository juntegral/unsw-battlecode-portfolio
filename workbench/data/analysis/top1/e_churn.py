#!/usr/bin/env python3
"""Does the leader's identity matter? Round-500 games with both queens dead.

A "leader cut" = a split in which the team's longest dragon (8+) keeps 2-3 segments and hands the rest to a new id.
  1. Games by the number of leader cuts from round 395 on (0 / 1-2 / 3-5 / 6+): games, wins, completeness at the end
     (final longest / final potential), growth of the longest from round 400 to the end, potential at round 400 as a
     share of the enemy's (the control), units left at the end. For meow, our opponents and each top team.
  2. 25-round windows from round 400 in which the team still has 10+ other dragons at the window start: growth of the
     longest dragon in the window, by whether a leader cut happened in the window or in the 25 rounds before it.
  3. meow, readable sonar only: growth of the longest dragon per 5 rounds from round 400, by the share of our dragons
     that believed the true longest at the start of those 5 rounds (while 10+ other dragons are left).
Reads e_out/w4. Output: e_out/churn.txt
"""
from collections import defaultdict

import e_data as D

P = None


def cuts(r, lo=395, hi=500):
    return [x for x in r.s["splits"] if x[7] and x[3] >= 8 and x[4] <= 3 and lo <= x[0] < hi]


def lend(r):
    return r.s["final"]["top"][0][0]


def pend(r):
    return lend(r) + r.s["final"]["pot"]


def pot(r, rnd, own=True):
    t = r.tl(rnd, own)
    return t[3] + t[12]


def part1(name, recs):
    if len(recs) < 6:
        return
    P("\n--- %s: %d games" % (name, len(recs)))
    P("    %-22s %5s %-14s %-18s %-22s %-22s %-12s %s" % ("leader cuts from r395", "games", "won", "c at the end", "longest r400 -> end", "own P / enemy P r400", "units end", "free cell at the cut"))
    for lab, lo, hi in (("none", 0, 0), ("1-2", 1, 2), ("3-5", 3, 5), ("6 or more", 6, 999)):
        v = [r for r in recs if lo <= len(cuts(r)) <= hi]
        if not v:
            continue
        allc = [x for r in v for x in cuts(r)]
        P("    %-22s %5d %-14s %-18s %-22s %-22s %-12s %s" % (
            lab, len(v), D.frac(sum(r.won for r in v), len(v)), D.med([lend(r) / max(1, pend(r)) for r in v], 2),
            "%s -> %s (+%s)" % (D.med([r.tl(400)[3] for r in v]), D.med([lend(r) for r in v]), D.med([lend(r) - r.tl(400)[3] for r in v])),
            D.med([pot(r, 400) / max(1, pot(r, 400, False)) for r in v], 2), D.med([r.s["final"]["units"] for r in v]),
            D.pct(sum(1 for x in allc if x[6] > 0), len(allc)) if allc else "-"))
    v = [len(cuts(r)) for r in recs]
    P("    leader cuts from round 395: mean %.2f a game, median %s; from round 300 to 394: mean %.2f; segments left behind in them from 395: mean %.1f" % (
        sum(v) / len(v), D.med(v), sum(len(cuts(r, 300, 395)) for r in recs) / len(recs), sum(x[4] for r in recs for x in cuts(r)) / len(recs)))


def part2(name, recs):
    acc = defaultdict(list)
    for r in recs:
        cs = [x[0] for x in cuts(r, 350)]
        for w in (400, 425, 450, 475):
            t0 = r.tl(w)
            t1 = r.tl(w + 20) if w == 475 else r.tl(w + 25)
            if t0[1] < 11:
                continue
            end_len = lend(r) if w == 475 else t1[3]
            g = end_len - t0[3]
            k = "a leader cut in the window or the 25 rounds before" if any(w - 25 <= c < w + 25 for c in cs) else "no leader cut"
            acc[k].append(g)
    if acc:
        P("    %s: 25-round windows from round 400 with 10+ other dragons left: " % name + "; ".join(
            "%s: %d windows, longest grows by median %s, mean %s" % (k, len(v), D.med(v), D.mean(v)) for k, v in sorted(acc.items())))


def part3(recs):
    acc = defaultdict(list)
    for r in recs:
        d = r.d
        if not (d["nping"] > 1000 and d["badping"] / d["nping"] < 0.05):
            continue
        tl = {row[0]: row for row in r.s["tl"]}
        for row in r.s["bel"]:
            rr = row[0]
            if rr < 400 or rr > 490 or row[1] < 10:
                continue
            a, b = tl.get(rr), tl.get(rr + 5)
            if not a or not b:
                continue
            share = row[2] / row[1]
            k = "under 25% believe the true longest" if share < 0.25 else "25-50%" if share < 0.5 else "50-75%" if share < 0.75 else "75% or more"
            acc[k].append(b[3] - a[3])
    P("\n--- meow, readable sonar, rounds 400-494, 10+ senders: growth of the longest dragon over the next 5 rounds")
    for k in ("under 25% believe the true longest", "25-50%", "50-75%", "75% or more"):
        v = acc[k]
        if v:
            P("    %-38s %4d samples: mean %+.2f, median %s; share with any growth %s" % (k, len(v), sum(v) / len(v), D.med(v), D.pct(sum(1 for x in v if x > 0), len(v))))


def main():
    global P
    P = D.Out("churn.txt")
    recs = D.rows()
    by = defaultdict(list)
    for r in recs:
        if not r.bd:
            continue
        for g in D.groups(r):
            by[g].append(r)
    for cls, cname in ((None, "all maps"), (False, "maps of 1,200 cells or fewer"), (True, "maps over 1,200 cells")):
        P("\n==================== %s ====================" % cname)
        for g in ("meow live", "meow test", "meow", "opp", "test4 (vs us)", "WHQ (vs us)", "forgot", "SSS", "Vibing++", "top3"):
            v = [r for r in by.get(g, []) if cls is None or r.big == cls]
            part1(g, v)
            part2(g, v)
    part3(by.get("meow", []))


if __name__ == "__main__":
    main()
