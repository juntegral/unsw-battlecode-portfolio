#!/usr/bin/env python3
"""Our games by bot era. The ladder bot changed during 4 October (the "stride" build went live); the marker that can be
read in a replay is the sonar format: readable leader pings = the earlier bot, sealed pings = stride and later.
For each era and run (round-500 games with both queens dead): games, wins, leader cuts from round 395, completeness at
the end, growth of the longest dragon in 25-round windows with / without a leader cut, the start of feeding.
Reads e_out/w4. Output: e_out/era.txt"""
from collections import defaultdict

import e_data as D
from e_churn import cuts, lend, pend, pot

P = D.Out("era.txt")


def readable(r):
    d = r.d
    return d["nping"] > 1000 and d["badping"] / d["nping"] < 0.05


def windows(recs):
    acc = defaultdict(list)
    for r in recs:
        cs = [x[0] for x in cuts(r, 350)]
        for w in (400, 425, 450, 475):
            t0 = r.tl(w)
            if t0[1] < 11:
                continue
            end_len = lend(r) if w == 475 else r.tl(w + 25)[3]
            acc[any(w - 25 <= c < w + 25 for c in cs)].append(end_len - t0[3])
    return acc


def line(name, recs):
    if not recs:
        return
    DI = {k: i for i, k in enumerate(recs[0].d["dcol"])}
    w = windows(recs)
    st = []
    for r in recs:
        rs = sorted(x[0] for x in r.s["deaths"] if x[DI["reason"]] == 4 and x[DI["akind"]] == 2 and not x[DI["tle"]])
        s = next((rs[i] for i in range(len(rs) - 2) if rs[i + 2] - rs[i] <= 15), None)
        st.append(s)
    P("%-34s %3d games, won %-14s | cuts from r395: mean %.1f | c at the end %s | longest r400 %s -> end %s | windows with a cut: %3d, growth mean %s; without: %3d, mean %s | "
      "feeding starts: median %s, before 390 in %d | own P / enemy P at r400 %s" % (
          name, len(recs), D.frac(sum(r.won for r in recs), len(recs)), sum(len(cuts(r)) for r in recs) / len(recs),
          D.med([lend(r) / max(1, pend(r)) for r in recs], 2), D.med([r.tl(400)[3] for r in recs]), D.med([lend(r) for r in recs]),
          len(w[True]), D.mean(w[True]), len(w[False]), D.mean(w[False]), D.med(st), sum(1 for s in st if s is not None and s < 390),
          D.med([pot(r, 400) / max(1, pot(r, 400, False)) for r in recs], 2)))


def main():
    recs = [r for r in D.rows() if r.me and r.study and r.bd]
    for cls, cname in ((None, "ALL MAPS"), (False, "MAPS OF 1,200 CELLS OR FEWER"), (True, "MAPS OVER 1,200 CELLS")):
        P("\n== %s (round-500 games with both queens dead)" % cname)
        v = [r for r in recs if cls is None or r.big == cls]
        line("readable sonar (earlier bot)", [r for r in v if readable(r)])
        line("sealed sonar (stride and later)", [r for r in v if not readable(r)])
        line("  sealed, live bot", [r for r in v if not readable(r) and r.build == "live"])
        line("  sealed, test builds", [r for r in v if not readable(r) and r.build != "live"])
        by = defaultdict(list)
        for r in v:
            by[r.set].append(r)
        for k in sorted(by):
            line("  run " + k, by[k])


if __name__ == "__main__":
    main()
