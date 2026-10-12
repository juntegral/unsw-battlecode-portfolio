#!/usr/bin/env python3
"""The leader-cut numbers of our bot separately against test4, against WeHaveQuizzes and against everybody else, and
separately for the live bot and the test builds (round-500 games with both queens dead):
  leader cuts from round 395 per game and the share made with a free cell; growth of the longest per 25-round window
  from round 400 with / without a cut (10+ other dragons left); completeness at the end; whom our feeders die next to;
  and, for games with readable sonar, the growth of the longest per 5 rounds by how many of our dragons believed it.
Reads e_out/w4. Output: e_out/opp.txt"""
from collections import Counter, defaultdict

import e_data as D
import e_lib as E

P = D.Out("opp.txt")


def cuts(r, lo=395, hi=500):
    return [x for x in r.s["splits"] if x[7] and x[3] >= 8 and x[4] <= 3 and lo <= x[0] < hi]


def lend(r):
    return r.s["final"]["top"][0][0]


def pend(r):
    return lend(r) + r.s["final"]["pot"]


def line(name, recs):
    if len(recs) < 3:
        return
    DI = {k: i for i, k in enumerate(recs[0].d["dcol"])}
    win = defaultdict(list)
    for r in recs:
        cs = [x[0] for x in cuts(r, 350)]
        for w in (400, 425, 450, 475):
            t0 = r.tl(w)
            if t0[1] < 11:
                continue
            end_len = lend(r) if w == 475 else r.tl(w + 25)[3]
            win[any(w - 25 <= c < w + 25 for c in cs)].append(end_len - t0[3])
    allc = [x for r in recs for x in cuts(r)]
    fd = [x for r in recs for x in r.s["deaths"] if x[DI["reason"]] == 4 and x[DI["akind"]] == 2 and not x[DI["tle"]]]
    tl = sum(1 for x in fd if x[DI["tlong"]] == 1)
    bel = defaultdict(list)
    for r in recs:
        d = r.d
        if not (d["nping"] > 1000 and d["badping"] / d["nping"] < 0.05):
            continue
        tlr = {row[0]: row for row in r.s["tl"]}
        for row in r.s["bel"]:
            rr = row[0]
            if rr < 400 or rr > 490 or row[1] < 10:
                continue
            a, b = tlr.get(rr), tlr.get(rr + 5)
            if a and b:
                bel[row[2] * 4 >= row[1]].append(b[3] - a[3])
    P("%-44s %3d games, won %2d | cuts from r395: %.1f a game, %s with a free cell | growth per 25 rounds with a cut %s (%d windows), without %s (%d) | c at the end %s | "
      "feeders next to the true longest %s of %d | growth per 5 rounds when under a quarter believe the true longest %s (%d samples), otherwise %s (%d)" % (
          name, len(recs), sum(r.won for r in recs), len(allc) / len(recs), D.pct(sum(1 for x in allc if x[6] > 0), len(allc)),
          D.mean(win[True]), len(win[True]), D.mean(win[False]), len(win[False]), D.med([lend(r) / max(1, pend(r)) for r in recs], 2),
          D.pct(tl, len(fd)), len(fd), D.mean(bel[False], 2), len(bel[False]), D.mean(bel[True], 2), len(bel[True])))


def main():
    recs = [r for r in D.rows() if r.me and r.study and r.bd]
    for bname, sel in (("all builds", lambda r: True), ("live bot", lambda r: r.build == "live"), ("test builds", lambda r: r.build != "live")):
        P("\n== %s" % bname)
        v = [r for r in recs if sel(r)]
        line("against test4", [r for r in v if r.opp == E.T4])
        line("against WeHaveQuizzes", [r for r in v if r.opp == E.WHQ])
        line("against everybody else", [r for r in v if r.opp not in (E.T4, E.WHQ)])
        line("maps of 1,200 cells or fewer", [r for r in v if not r.big])
        line("maps over 1,200 cells", [r for r in v if r.big])
        line("all", v)
    P("\n== by map (all builds)")
    by = defaultdict(list)
    for r in recs:
        by[r.map].append(r)
    for m in sorted(by):
        line(m, by[m])


if __name__ == "__main__":
    main()
