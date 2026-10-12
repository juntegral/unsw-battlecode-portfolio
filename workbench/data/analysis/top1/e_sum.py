#!/usr/bin/env python3
"""Compact markdown tables for deep-read-5.md, section 2 (all numbers are medians per game unless a cell says mean).
Round-500 games with both queens dead, for meow (live bot / test builds), our opponents in the same games, forgot, SSS,
Vibing++, and test4 / WeHaveQuizzes against us; by map class. Reads e_out/w4. Output: e_out/sum_tables.md
Words: P = potential = longest + pearls all other own dragons would drop (sum of ceil(L/2)); c = longest / P;
lineage = the final longest dragon followed back through splits; leader cut = a split in which the team's longest (8+)
keeps 2-3 segments and the rest becomes a new id; feeder = a death by choice within 3 path steps of an own dragon at
least twice as long (for meow: also every `noaction` death)."""
from collections import Counter, defaultdict

import e_data as D
import e_lib as E

OUT = D.Out("sum_tables.md")
GROUPS = ("meow live", "meow test", "opp", "test4 (vs us)", "WHQ (vs us)", "forgot", "SSS", "Vibing++")
NAMES = {"meow live": "meow live bot", "meow test": "meow test builds", "opp": "our opponents", "test4 (vs us)": "test4 (vs us)",
         "WHQ (vs us)": "WHQ (vs us)", "forgot": "forgot", "SSS": "SSS", "Vibing++": "Vibing++", "meow": "meow (all)", "top3": "top three"}


def lend(r, own=True):
    f = (r.s if own else r.o)["final"]
    return f["top"][0][0] if f["top"] else 0


def pend(r, own=True):
    return lend(r, own) + (r.s if own else r.o)["final"]["pot"]


def pot(r, rnd, own=True):
    t = r.tl(rnd, own)
    return t[3] + t[12]


def cuts(r, lo=395, hi=500):
    return [x for x in r.s["splits"] if x[7] and x[3] >= 8 and x[4] <= 3 and lo <= x[0] < hi]


def feeder(x, DI, me):
    if x[DI["cls"]] == 2 and 0 <= x[DI["tdist"]] <= 3:
        return True
    return me and x[DI["reason"]] == 4 and x[DI["akind"]] == 2 and not x[DI["tle"]]


def start_of(r, DI):
    rs = sorted(x[0] for x in r.s["deaths"] if feeder(x, DI, r.me) and x[DI["tq"]] != 1)
    for i in range(len(rs) - 2):
        if rs[i + 2] - rs[i] <= 15:
            return rs[i]
    return None


def takeoff(tl, gain=8, span=25, r_from=100):
    k = span // 5
    for i in range(r_from // 5, len(tl) - k):
        if tl[i + k][3] - tl[i][3] >= gain:
            j = min(len(tl) - 1, i + 10)
            return tl[i][0], tl[j][3] - tl[i][3]
    return None, None


def m(v, nd=0):
    return D.med(v, nd)


def row(cells):
    OUT("| " + " | ".join(str(c) for c in cells) + " |")


def head(cols):
    row(cols)
    row(["---"] * len(cols))


def main():
    recs = D.rows()
    by = defaultdict(list)
    for r in recs:
        for g in D.groups(r):
            by[g].append(r)
    DI = {k: i for i, k in enumerate(recs[0].d["dcol"])}
    for cls, cname in ((False, "maps of 1,200 cells or fewer"), (True, "maps over 1,200 cells")):
        gs = {g: [r for r in by.get(g, []) if r.bd and r.big == cls] for g in GROUPS + ("meow", "top3")}
        OUT("\n### %s\n" % cname.capitalize())
        OUT("**Table A1 (%s). The curve.** Round-500 games with both queens dead, all of them. Medians.\n" % cname)
        head(["group", "games", "won", "longest at 200 / 250 / 300 / 350 / 400 / 450 / end", "enemy's longest at 300 / 400 / end",
              "units 300 / 400 / end", "total length 300 / 400 / end", "P (potential) 300 / 400 / end", "c = longest / P at 400 / 450 / end"])
        for g in GROUPS:
            v = gs[g]
            if not v:
                continue
            row([NAMES[g], len(v), sum(r.won for r in v),
                 " / ".join(m([r.tl(x)[3] for r in v]) for x in (200, 250, 300, 350, 400, 450)) + " / " + m([lend(r) for r in v]),
                 " / ".join(m([r.tl(x, False)[3] for r in v]) for x in (300, 400)) + " / " + m([lend(r, False) for r in v]),
                 " / ".join(m([r.tl(x)[1] for r in v]) for x in (300, 400)) + " / " + m([r.s["final"]["units"] for r in v]),
                 " / ".join(m([r.tl(x)[2] for r in v]) for x in (300, 400)) + " / " + m([r.s["final"]["total"] for r in v]),
                 " / ".join(m([pot(r, x) for r in v]) for x in (300, 400)) + " / " + m([pend(r) for r in v]),
                 " / ".join(m([r.tl(x)[3] / max(1, pot(r, x)) for r in v], 2) for x in (400, 450)) + " / " + m([lend(r) / max(1, pend(r)) for r in v], 2)])
        OUT("\n**Table A2 (%s). The same at level potential** (own P / enemy P at round 400 between 0.8 and 1.25).\n" % cname)
        head(["group", "games", "won", "longest at 300 / 350 / 400 / 450 / end", "enemy's longest at 300 / 350 / 400 / 450 / end", "P at 300 / 400 / end, own : enemy",
              "c at 400 / 450 / end, own : enemy", "units at 400 / end, own : enemy"])
        for g in GROUPS:
            v = [r for r in gs[g] if 0.8 <= pot(r, 400) / max(1, pot(r, 400, False)) < 1.25]
            if len(v) < 3:
                continue
            row([NAMES[g], len(v), sum(r.won for r in v),
                 " / ".join(m([r.tl(x)[3] for r in v]) for x in (300, 350, 400, 450)) + " / " + m([lend(r) for r in v]),
                 " / ".join(m([r.tl(x, False)[3] for r in v]) for x in (300, 350, 400, 450)) + " / " + m([lend(r, False) for r in v]),
                 " / ".join("%s : %s" % (m([pot(r, x) for r in v]), m([pot(r, x, False) for r in v])) for x in (300, 400)) + " / %s : %s" % (
                     m([pend(r) for r in v]), m([pend(r, False) for r in v])),
                 " / ".join("%s : %s" % (m([r.tl(x)[3] / max(1, pot(r, x)) for r in v], 2), m([r.tl(x, False)[3] / max(1, pot(r, x, False)) for r in v], 2)) for x in (400, 450))
                 + " / %s : %s" % (m([lend(r) / max(1, pend(r)) for r in v], 2), m([lend(r, False) / max(1, pend(r, False)) for r in v], 2)),
                 "%s : %s / %s : %s" % (m([r.tl(400)[1] for r in v]), m([r.tl(400, False)[1] for r in v]), m([r.s["final"]["units"] for r in v]), m([r.o["final"]["units"] for r in v]))])
        OUT("\n**Table A3 (%s). When it starts and how fast.** Start of leader feeding = first of three feeder deaths within 15 rounds; take-off = first round from which the "
            "longest dragon grows by 8+ within 25 rounds.\n" % cname)
        head(["group", "games", "longest first 8 / 15 / 25 long (median round; never)", "lineage first 8 / 15 / 25 long", "start of leader feeding: quartile / median / quartile (games without)",
              "take-off: median round (never)", "growth of the longest in the 50 rounds after take-off", "growth of the longest from round 400 to the end"])
        for g in GROUPS:
            v = gs[g]
            if not v:
                continue
            st = [start_of(r, DI) for r in v]
            sv = sorted(s for s in st if s is not None)
            to = [takeoff(r.s["tl"]) for r in v]

            def fr(key, T):
                a = [r.s[key].get(str(T)) if key == "longfirst" else r.s["lin"]["first"].get(str(T)) for r in v]
                return "%s (%d)" % (m(a), sum(x is None for x in a))
            row([NAMES[g], len(v), " / ".join(fr("longfirst", T) for T in (8, 15, 25)), " / ".join(fr("lin", T) for T in (8, 15, 25)),
                 ("%d / %d / %d (%d)" % (sv[len(sv) // 4], sv[len(sv) // 2], sv[(3 * len(sv)) // 4], len(st) - len(sv))) if sv else "-",
                 "%s (%d)" % (m([t[0] for t in to]), sum(t[0] is None for t in to)), m([t[1] for t in to]), m([lend(r) - r.tl(400)[3] for r in v])])
        OUT("\n**Table B1 (%s). Where the final longest dragon's length comes from** (its lineage; mean pearls per game in rounds 250-299 / 300-349 / 350-399 / 400-449 / 450-499).\n" % cname)
        head(["group", "natural pearls", "pearls of own dragons dead by choice", "pearls of other own corpses (boxed in, rammed)", "pearls of enemy corpses",
              "segments left behind in leader cuts", "whole team: natural pearls eaten", "whole team: length of dragons dead by choice"])
        for g in GROUPS:
            v = gs[g]
            if not v:
                continue
            n = len(v)

            def e(role, codes):
                return " / ".join("%.1f" % (sum(sum(r.s["eats"].get("%s|%d|%d" % (role, b, c), 0) for c in codes) for r in v) / n) for b in range(5, 10))
            row([NAMES[g], e("N", (0,)), e("N", (1,)), e("N", (2, 3)), e("N", (4, 5, 6)),
                 " / ".join("%.1f" % (sum(sum(h[3] - h[4] for h in r.s["lin"]["hand"] if h[0] // 50 == b and h[3] >= 8) for r in v) / n) for b in range(5, 10)),
                 e("T", (0,)),
                 " / ".join("%.0f" % (sum(sum(x[2] for x in r.s["deaths"] if x[DI["cls"]] == 2 and x[0] // 50 == b) for r in v) / n) for b in range(5, 10))])
        OUT("\n**Table B2 (%s). Feeders from round 250.**\n" % cname)
        head(["group", "feeders a game", "mean length", "pearls dropped a game", "eaten by the dragon fed", "by other own dragons", "by the enemy", "by nobody",
              "the dragon fed is the team's longest", "is under 10 long", "path steps to the fed dragon's head: 1 / 2 / 3 / more or none", "nearest enemy head (median cells)",
              "final lineage's gain per feeder segment"])
        for g in GROUPS:
            v = gs[g]
            if not v:
                continue
            me = g.startswith("meow")
            fd = [x for r in v for x in r.s["deaths"] if feeder(x, DI, me and True) and x[0] >= 250] if me else \
                [x for r in v for x in r.s["deaths"] if feeder(x, DI, False) and x[0] >= 250]
            if not fd:
                continue
            L = sum(x[2] for x in fd)
            dr = sum(x[DI["drop"]] for x in fd)
            et = sum(x[DI["e_t"]] + x[DI["e_l"]] for x in fd)
            eo = sum(x[DI["e_o"]] + x[DI["e_q"]] for x in fd)
            ee = sum(x[DI["e_e"]] for x in fd)
            dc = Counter(x[DI["tdist"]] if 1 <= x[DI["tdist"]] <= 3 else 9 for x in fd)
            row([NAMES[g], "%.1f" % (len(fd) / len(v)), "%.2f" % (L / len(fd)), "%.1f" % (dr / len(v)), D.pct(et, dr), D.pct(eo, dr), D.pct(ee, dr, 1), D.pct(dr - et - eo - ee, dr),
                 D.pct(sum(1 for x in fd if x[DI["tlong"]] == 1), len(fd)), D.pct(sum(1 for x in fd if x[DI["tlen"]] < 10), len(fd)),
                 " / ".join(D.pct(dc[k], len(fd)) for k in (1, 2, 3, 9)), m([x[DI["emanh"]] for x in fd]), "%.2f" % (sum(x[DI["e_lin"]] for x in fd) / L)])
        OUT("\n**Table C1 (%s). Who the leader is and whether it lasts.**\n" % cname)
        head(["group", "longest at round 400 is the final longest: same id / same lineage", "at round 450", "leader cuts a game, rounds 300-394 / 395-499", "of the cuts from 395: made with a free cell",
              "growth of the longest per 25 rounds from 400 (10+ other dragons left): windows with a cut in them or just before / without (number of windows)",
              "longest dragon (15+) died: per game (rammed / boxed in / by choice / own ram)", "leader at 400 / 450: cells to the nearest enemy head", "steps it took per 25 rounds at 400 / 450",
              "end: second longest / longest", "units at the end"])
        for g in GROUPS:
            v = gs[g]
            if not v:
                continue
            n = len(v)
            same = lambda r0: "%s / %s" % (D.pct(sum(r.tl(r0)[4] == r.s["lin"]["id"] for r in v), n), D.pct(sum(r.s["lin"]["ids"][r0 // 5] == r.tl(r0)[4] for r in v), n))
            allc = [x for r in v for x in cuts(r)]
            win = defaultdict(list)
            for r in v:
                cs = [x[0] for x in cuts(r, 350)]
                for w in (400, 425, 450, 475):
                    t0 = r.tl(w)
                    if t0[1] < 11:
                        continue
                    end_len = lend(r) if w == 475 else r.tl(w + 25)[3]
                    win[any(w - 25 <= c < w + 25 for c in cs)].append(end_len - t0[3])
            kinds = Counter()
            for r in v:
                for x in r.s["deaths"]:
                    if x[DI["rank"]] == 1 and x[2] >= 15:
                        kinds[x[DI["cls"]]] += 1
            lead = lambda r0, col: m([row_[col] for r in v for row_ in r.s["lead"] if row_[0] == r0])
            steps = {}
            for r0 in (400, 450):
                vals = []
                for r in v:
                    L = {row_[0]: row_ for row_ in r.s["lead"]}
                    a, b = L.get(r0 - 25), L.get(r0)
                    if a and b and a[1] == b[1]:
                        vals.append(b[14] - a[14])
                steps[r0] = D.mean(vals, 0)
            row([NAMES[g], same(400), same(450), "%.1f / %.1f" % (sum(len(cuts(r, 300, 395)) for r in v) / n, len(allc) / n),
                 D.pct(sum(1 for x in allc if x[6] > 0), len(allc)),
                 "%s / %s (%d / %d)" % (D.mean(win[True]), D.mean(win[False]), len(win[True]), len(win[False])),
                 "%.2f (%d / %d / %d / %d)" % (sum(kinds.values()) / n, kinds[0], kinds[3], kinds[2], kinds[1]),
                 "%s / %s" % (lead(400, 6), lead(450, 6)), "%s / %s" % (steps[400], steps[450]),
                 m([(r.s["final"]["top"][1][0] if len(r.s["final"]["top"]) > 1 else 0) / max(1, lend(r)) for r in v], 2), m([r.s["final"]["units"] for r in v])])
    # the footing: all maps
    OUT("\n### The footing: potential and completeness, all maps\n")
    head(["group", "round-500 games with both queens dead", "won", "own P / enemy P at 300 / 400 / end (median)", "won with P ratio at round 400 under 0.5", "0.5-0.8", "0.8-1.0", "1.0-1.25", "over 1.25",
          "c at the end, own : enemy, in the 0.8-1.25 games"])
    for g in ("meow live", "meow test", "meow", "opp", "test4 (vs us)", "WHQ (vs us)", "forgot", "SSS", "Vibing++", "top3"):
        v = [r for r in by.get(g, []) if r.bd]
        if not v:
            continue
        cells = []
        for lo, hi in ((0, 0.5), (0.5, 0.8), (0.8, 1.0), (1.0, 1.25), (1.25, 99)):
            w = [r for r in v if lo <= pot(r, 400) / max(1, pot(r, 400, False)) < hi]
            cells.append("%d of %d" % (sum(r.won for r in w), len(w)))
        lv = [r for r in v if 0.8 <= pot(r, 400) / max(1, pot(r, 400, False)) < 1.25]
        row([NAMES[g], len(v), sum(r.won for r in v),
             " / ".join(m([pot(r, x) / max(1, pot(r, x, False)) for r in v], 2) for x in (300, 400)) + " / " + m([pend(r) / max(1, pend(r, False)) for r in v], 2)]
            + cells + ["%s : %s" % (m([lend(r) / max(1, pend(r)) for r in lv], 2), m([lend(r, False) / max(1, pend(r, False)) for r in lv], 2))])


if __name__ == "__main__":
    main()
