#!/usr/bin/env python3
"""Question (b): where the leader's length comes from, per 50 rounds. Round-500 games with both queens dead.

Per group and map class, means per game for each 50-round block from round 150:
  LEADER rows   pearls eaten by the lineage (the final longest dragon followed back) and by the leader of the time:
                natural / of own dragons that died by choice / of other own corpses (boxed or rammed) / of enemy corpses;
                segments it paid for extra steps; segments the lineage left behind in handovers and gave away in sheds.
  TEAM rows     natural pearls the whole team ate; deaths by choice (number, summed length); of those "feeders" = died
                within F path steps of an own dragon at least twice as long (number, length, pearls dropped) and where
                those pearls went: that dragon / the leader of the time (if another) / other own / the enemy / nobody;
                the gain of the fed dragon per feeder segment spent.
  Then: the distance at which feeders die from the dragon they feed, and how far the nearest enemy head is.
Definitions: "by choice" = a death that is not a ram, of a dragon that had a free cell next to its head at the start of
its turn. Reads e_out/w. Output: e_out/b_source.txt     Usage: python3 e_b.py [F=3]
"""
import sys
from collections import Counter, defaultdict

import e_data as D

F = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 3
P = D.Out("b_source.txt")
BINS = list(range(3, 10))


def eat(s, role, b, codes):
    return sum(s["eats"].get("%s|%d|%d" % (role, b, c), 0) for c in codes)


MEOW = [False]


def is_feeder(x, DI, f=F):
    """By choice within f path steps of an own dragon twice as long; for meow also every `noaction` death
    (our bot's feeder deaths: it returns without an order), wherever it happened."""
    if x[DI["cls"]] == 2 and 0 <= x[DI["tdist"]] <= f:
        return True
    return MEOW[0] and x[DI["reason"]] == 4 and x[DI["akind"]] == 2 and not x[DI["tle"]]


def block(recs, title):
    n = len(recs)
    if not n:
        return
    MEOW[0] = title.startswith("meow")
    P("\n--- %s: %d games, won %d" % (title, n, sum(r.won for r in recs)))
    DI = {k: i for i, k in enumerate(recs[0].d["dcol"])}
    head = "    %-58s" % "per game, rounds" + "".join("%9s" % ("%d-%d" % (b * 50, b * 50 + 49)) for b in BINS) + "%9s" % "150-499"

    def row(name, fn, nd=1):
        vals = [sum(fn(r, b) for r in recs) / n for b in BINS]
        P("    %-58s" % name + "".join("%9.*f" % (nd, v) for v in vals) + "%9.*f" % (nd, sum(vals)))

    P(head)
    for role, nm in (("N", "LINEAGE"), ("L", "LEADER OF THE TIME")):
        row("%s eats: natural pearls" % nm, lambda r, b: eat(r.s, role, b, (0,)))
        row("%s eats: pearls of own dragons dead by choice" % nm, lambda r, b: eat(r.s, role, b, (1,)))
        row("%s eats: pearls of own dragons boxed in" % nm, lambda r, b: eat(r.s, role, b, (2,)))
        row("%s eats: pearls of own dragons dead in rams" % nm, lambda r, b: eat(r.s, role, b, (3,)))
        row("%s eats: pearls of enemy corpses" % nm, lambda r, b: eat(r.s, role, b, (4, 5, 6)))
        row("%s pays for extra steps (segments)" % nm, lambda r, b: r.s["paid"].get("%s|%d" % (role, b), 0))
    row("LINEAGE left behind in handovers to a split child", lambda r, b: sum(h[3] - h[4] for h in r.s["lin"]["hand"] if h[0] // 50 == b))
    row("LINEAGE gave away in sheds (it stayed the parent)", lambda r, b: r.s["lin"]["shed"].get(str(b), 0))
    row("LEADER OF THE TIME: splits (number)", lambda r, b: sum(1 for x in r.s["splits"] if x[7] and x[0] // 50 == b), 2)
    row("TEAM eats natural pearls", lambda r, b: eat(r.s, "T", b, (0,)))
    row("TEAM eats pearls of own corpses", lambda r, b: eat(r.s, "T", b, (1, 2, 3)))
    row("TEAM eats pearls of enemy corpses", lambda r, b: eat(r.s, "T", b, (4, 5, 6)))
    row("ENEMY eats pearls of this team's corpses", lambda r, b: eat(r.o, "T", b, (4, 5, 6)))
    row("deaths by choice: number", lambda r, b: sum(1 for x in r.s["deaths"] if x[DI["cls"]] == 2 and x[0] // 50 == b))
    row("deaths by choice: summed length", lambda r, b: sum(x[2] for x in r.s["deaths"] if x[DI["cls"]] == 2 and x[0] // 50 == b))
    row("feeders (by choice, <=%d steps from an own 2x dragon): number" % F, lambda r, b: sum(1 for x in r.s["deaths"] if is_feeder(x, DI) and x[0] // 50 == b))
    row("feeders: summed length", lambda r, b: sum(x[2] for x in r.s["deaths"] if is_feeder(x, DI) and x[0] // 50 == b))
    row("feeders: pearls dropped", lambda r, b: sum(x[DI["drop"]] for x in r.s["deaths"] if is_feeder(x, DI) and x[0] // 50 == b))
    row("   eaten by the dragon they died next to", lambda r, b: sum(x[DI["e_t"]] for x in r.s["deaths"] if is_feeder(x, DI) and x[0] // 50 == b))
    row("   eaten by the leader of the time (if another)", lambda r, b: sum(x[DI["e_l"]] for x in r.s["deaths"] if is_feeder(x, DI) and x[0] // 50 == b))
    row("   eaten by other own dragons", lambda r, b: sum(x[DI["e_o"]] + x[DI["e_q"]] for x in r.s["deaths"] if is_feeder(x, DI) and x[0] // 50 == b))
    row("   eaten by the enemy", lambda r, b: sum(x[DI["e_e"]] for x in r.s["deaths"] if is_feeder(x, DI) and x[0] // 50 == b))
    row("   eaten by the lineage (any of the above)", lambda r, b: sum(x[DI["e_lin"]] for x in r.s["deaths"] if is_feeder(x, DI) and x[0] // 50 == b))
    row("boxed-in deaths: number", lambda r, b: sum(v[0] for k, v in r.s["dagg"].items() if k.split("|")[0] == str(b) and k.split("|")[1] == "3"))
    row("rammed by the enemy: number", lambda r, b: sum(v[0] for k, v in r.s["dagg"].items() if k.split("|")[0] == str(b) and k.split("|")[1] == "0"))
    row("rammed by the enemy: summed length", lambda r, b: sum(v[1] for k, v in r.s["dagg"].items() if k.split("|")[0] == str(b) and k.split("|")[1] == "0"))
    row("it rammed an enemy: number", lambda r, b: sum(v[0] for k, v in r.s["dagg"].items() if k.split("|")[0] == str(b) and k.split("|")[1] == "1"))
    # totals from round 300
    fd = [x for r in recs for x in r.s["deaths"] if is_feeder(x, DI) and x[0] >= 250]
    if fd:
        L = sum(x[2] for x in fd)
        dr = sum(x[DI["drop"]] for x in fd)
        et, el, eo, ee, en = (sum(x[DI[k]] for x in fd) for k in ("e_t", "e_l", "e_o", "e_e", "e_lin"))
        eo += sum(x[DI["e_q"]] for x in fd)
        P("    feeders from round 250: %d (%.1f a game), mean length %.2f; pearls dropped %d = %.0f%% of their length; eaten by the dragon fed %s, "
          "the leader of the time otherwise %s, other own %s, enemy %s, nobody %s; fed dragon's gain per feeder segment %.2f (lineage's %.2f)" % (
              len(fd), len(fd) / n, L / len(fd), dr, 100.0 * dr / L, D.pct(et, dr), D.pct(el, dr), D.pct(eo, dr), D.pct(ee, dr),
              D.pct(dr - et - el - eo - ee, dr), (et + el) / L, en / L))
        dist = Counter(x[DI["tdist"]] for x in fd)
        P("    path steps from the dying feeder's head to the head of the dragon fed: " + ", ".join("%d: %s" % (k, D.pct(dist[k], len(fd))) for k in sorted(dist)))
        tl = Counter(min(x[DI["tlen"]] // 10, 6) for x in fd)
        P("    length of the dragon fed at that moment: " + ", ".join("%s: %s" % ("%d-%d" % (k * 10, k * 10 + 9) if k < 6 else "60+", D.pct(tl[k], len(fd))) for k in sorted(tl)))
        P("    the dragon fed is the team's longest: %s; is the queen: %s" % (D.pct(sum(x[DI["tlong"]] == 1 for x in fd), len(fd)), D.pct(sum(x[DI["tq"]] == 1 for x in fd), len(fd))))
        em = [x[DI["emanh"]] for x in fd]
        P("    nearest enemy head at that moment (cells, Manhattan): median %s; within 4: %s; within 8: %s; none within 15: %s" % (
            D.med(em), D.pct(sum(e <= 4 for e in em), len(em)), D.pct(sum(e <= 8 for e in em), len(em)), D.pct(sum(e > 15 for e in em), len(em))))
        fl = Counter(min(x[2], 10) for x in fd)
        P("    feeder length: " + ", ".join("%s: %s" % (k if k < 10 else "10+", D.pct(fl[k], len(fd))) for k in sorted(fl)))
        rs = Counter(("suicide order" if x[DI["akind"]] == 2 else "unpayable move" if x[DI["reason"]] == 4 else ("wall", "own body", "another body")[x[DI["reason"]]]) for x in fd)
        P("    how they die: " + ", ".join("%s %s" % (k, D.pct(v, len(fd))) for k, v in rs.most_common()))
    # all by-choice deaths: where
    ch = [x for r in recs for x in r.s["deaths"] if x[DI["cls"]] == 2 and x[0] >= 250]
    if ch:
        c = Counter(("no own 2x dragon within 8 steps" if x[DI["tdist"]] < 0 else "%d" % x[DI["tdist"]]) for x in ch)
        P("    all deaths by choice from round 250 (%d, %.1f a game) by path steps to the nearest own dragon twice as long: %s" % (
            len(ch), len(ch) / n, ", ".join("%s: %s" % (k, D.pct(c[k], len(ch))) for k in sorted(c, key=lambda z: (len(z) > 2, z)))))


def main():
    recs = D.rows()
    by = defaultdict(list)
    for r in recs:
        for g in D.groups(r):
            by[g].append(r)
    order = list(D.ORDER) + ["top3 vs t4/WHQ", "test4 (vs us)", "WHQ (vs us)", "test4 (vs top3)", "WHQ (vs top3)"]
    for cls, name in ((False, "MAPS OF 1,200 CELLS OR FEWER"), (True, "MAPS OVER 1,200 CELLS")):
        P("\n\n==================== %s: round-500 games with both queens dead ====================" % name)
        for g in order:
            v = [r for r in by.get(g, []) if r.bd and r.big == cls]
            if not v:
                continue
            block(v, "%s | all such games" % g)
            lv = [r for r in v if D.band400(r) == "0.8-1.25"]
            if len(lv) >= 4:
                block(lv, "%s | total length level at round 400 (0.8-1.25)" % g)


if __name__ == "__main__":
    main()
