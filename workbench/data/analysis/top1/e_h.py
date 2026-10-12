#!/usr/bin/env python3
"""Question (h): the risks, counted. All study games (any ending) unless said.

  1. Leader rammed: deaths of the team's longest dragon by an enemy ram, per 1,000 rounds in which the team's longest was
     in that length band, by round block; and what share of all leader losses were rams / boxed / by choice / own rams.
  2. What feeding costs: units, total length, potential and natural pearls eaten per 50 rounds, aligned on the start of
     leader feeding (rounds -100..+150 around it), per team.
  3. Who starts first: games in which one side starts leader feeding at least 25 rounds before the other (or the other
     never does): how the game ends for the earlier side (wipe-out win / loss, queen rule, longest rule).
  4. Feeder pearls that go to the enemy: by how far the nearest enemy head is when the feeder dies, per team.
Feeding start = first of three "leader feeder" deaths within 15 rounds (by choice, within 3 path steps of an own dragon
twice as long that is not the queen); for meow also its `noaction` deaths. Reads e_out/w4. Output: e_out/h_risk.txt
"""
from collections import Counter, defaultdict

import e_data as D
import e_lib as E

P = D.Out("h_risk.txt")
BANDS = ((15, 24), (25, 39), (40, 999))
RB = ((150, 299), (300, 399), (400, 499))


def feeder(x, DI, me):
    if x[DI["cls"]] == 2 and 0 <= x[DI["tdist"]] <= 3 and x[DI["tq"]] != 1:
        return True
    return me and x[DI["reason"]] == 4 and x[DI["akind"]] == 2 and not x[DI["tle"]]


def start_of(r, DI):
    rs = sorted(x[0] for x in r.s["deaths"] if feeder(x, DI, r.me))
    for i in range(len(rs) - 2):
        if rs[i + 2] - rs[i] <= 15:
            return rs[i]
    return None


def start_other(r, DI):
    me = r.d["me"] == E.other(r.S)
    rs = sorted(x[0] for x in r.o["deaths"] if feeder(x, DI, me))
    for i in range(len(rs) - 2):
        if rs[i + 2] - rs[i] <= 15:
            return rs[i]
    return None


def part1(name, recs):
    DI = {k: i for i, k in enumerate(recs[0].d["dcol"])}
    P("\n--- %s: %d games" % (name, len(recs)))
    for lo, hi in BANDS:
        line = "    leader %d-%s long:" % (lo, hi if hi < 999 else "+")
        for a, b in RB:
            rounds = 0
            kinds = Counter()
            for r in recs:
                rounds += 5 * sum(1 for row in r.s["tl"] if a <= row[0] <= b and lo <= row[3] <= hi)
                for x in r.s["deaths"]:
                    if x[DI["rank"]] == 1 and lo <= x[2] <= hi and a <= x[0] <= b:
                        kinds[x[DI["cls"]]] += 1
            line += "  r%d-%d: %d rammed in %d leader-rounds = %.1f per 1,000 (boxed %d, by choice %d, own ram %d)" % (
                a, b, kinds[0], rounds, 1000.0 * kinds[0] / max(1, rounds), kinds[3], kinds[2], kinds[1])
        P(line)
    kl = Counter()
    for r in recs:
        for x in r.s["deaths"]:
            if x[DI["rank"]] == 1 and x[2] >= 15 and x[DI["cls"]] == 0:
                k = x[DI["klen"]]
                kl["2-4" if k <= 4 else "5-9" if k <= 9 else "10+"] += 1
    P("    length of the enemy that rammed a leader of 15+: %s; steps it took: see the rows" % dict(kl))


def part2(name, recs):
    DI = {k: i for i, k in enumerate(recs[0].d["dcol"])}
    rows = [(r, start_of(r, DI)) for r in recs if r.rounds >= 500]
    have = [(r, st) for r, st in rows if st is not None and 150 <= st <= 425]
    if len(have) < 8:
        return
    P("\n--- %s: %d round-500 games with a start of leader feeding between rounds 150 and 425 (median start %s)" % (
        name, len(have), D.med([st for r, st in have])))
    offs = (-100, -50, 0, 25, 50, 75, 100)
    P("    rounds relative to the start:              " + "".join("%8d" % o for o in offs))
    for lab, fn in (("units", lambda t: t[1]), ("total length", lambda t: t[2]), ("longest", lambda t: t[3]), ("potential (longest + pearls of the rest)", lambda t: t[3] + t[12])):
        line = "    %-44s" % lab
        for o in offs:
            v = [fn(r.tl((st + o) // 5 * 5)) for r, st in have if 0 <= st + o < 500 and r.tl((st + o) // 5 * 5)]
            line += "%8s" % D.med(v)
        P(line)
    line = "    %-44s" % "natural pearls eaten in the 50 rounds before"
    for o in offs:
        v = []
        for r, st in have:
            b = (st + o) // 50 - 1
            if 0 <= b <= 9:
                v.append(r.s["eats"].get("T|%d|0" % b, 0))
        line += "%8s" % D.med(v)
    P(line)
    line = "    %-44s" % "ENEMY's potential"
    for o in offs:
        v = [(lambda t: t[3] + t[12])(r.tl((st + o) // 5 * 5, False)) for r, st in have if 0 <= st + o < 500 and r.tl((st + o) // 5 * 5, False)]
        line += "%8s" % D.med(v)
    P(line)


def part3(recs):
    DI = {k: i for i, k in enumerate(recs[0].d["dcol"])}
    P("\n--- who starts leader feeding first (one row per game, counted from the side that starts at least 25 rounds earlier, or alone)")
    for gname, sel in (("top-three sides", lambda r: r.team in E.TOP3 and r.study), ("meow sides", lambda r: r.team == E.ME and r.study),
                       ("our opponents' sides", lambda r: r.opp == E.ME and r.map != "Schooltime" and r.d[r.S + "e"] >= 2000)):
        c = Counter()
        for r in recs:
            if not sel(r) or r.rounds < 300:
                continue
            a, b = start_of(r, DI), start_other(r, DI)
            if a is None and b is None:
                k = "neither side starts"
            elif b is None or (a is not None and a <= b - 25):
                k = "this side first"
            elif a is None or b <= a - 25:
                k = "the other side first"
            else:
                k = "within 25 rounds of each other"
            end = "wipe-out" if not r.r500 else "queen rule" if (r.qa or r.eqa) else "longest"
            c[(k, end, r.won)] += 1
        P("    %s:" % gname)
        for k in ("this side first", "the other side first", "within 25 rounds of each other", "neither side starts"):
            tot = sum(v for (kk, e, w), v in c.items() if kk == k)
            if not tot:
                continue
            P("       %-32s %4d games, won %-14s | longest rule: won %d of %d | queen rule: won %d of %d | wipe-out: won %d of %d" % (
                k, tot, D.frac(sum(v for (kk, e, w), v in c.items() if kk == k and w), tot),
                c[(k, "longest", True)], c[(k, "longest", True)] + c[(k, "longest", False)],
                c[(k, "queen rule", True)], c[(k, "queen rule", True)] + c[(k, "queen rule", False)],
                c[(k, "wipe-out", True)], c[(k, "wipe-out", True)] + c[(k, "wipe-out", False)]))


def part4(name, recs):
    DI = {k: i for i, k in enumerate(recs[0].d["dcol"])}
    acc = defaultdict(lambda: [0, 0, 0, 0, 0])
    for r in recs:
        for x in r.s["deaths"]:
            if not feeder(x, DI, r.me) or x[0] < 150:
                continue
            e = x[DI["emanh"]]
            k = "enemy head within 4 cells" if e <= 4 else "5-8 cells" if e <= 8 else "9-15 cells" if e <= 15 else "farther than 15"
            a = acc[k]
            a[0] += 1
            a[1] += x[DI["drop"]]
            a[2] += x[DI["e_e"]]
            a[3] += x[DI["e_t"]] + x[DI["e_l"]]
            a[4] += x[2]
    tot = sum(a[0] for a in acc.values())
    if not tot:
        return
    P("    %s: %d feeders (%.1f a game), %d pearls, %s eaten by the enemy" % (
        name, tot, tot / len(recs), sum(a[1] for a in acc.values()), D.pct(sum(a[2] for a in acc.values()), sum(a[1] for a in acc.values()), 1)))
    for k in ("enemy head within 4 cells", "5-8 cells", "9-15 cells", "farther than 15"):
        a = acc[k]
        if a[0]:
            P("       %-28s %5d feeders = %s | pearls %5d: the enemy ate %s, the fed dragon %s" % (
                k, a[0], D.pct(a[0], tot), a[1], D.pct(a[2], a[1], 1), D.pct(a[3], a[1])))


def main():
    recs = D.rows()
    by = defaultdict(list)
    for r in recs:
        for g in D.groups(r):
            by[g].append(r)
    P("PART 1: the team's longest dragon rammed by an enemy")
    for g in ("meow live", "meow test", "opp", "forgot", "SSS", "Vibing++"):
        if by.get(g):
            part1(g, by[g])
    P("\n\nPART 2: what feeding costs, aligned on its start")
    for g in ("meow live", "meow test", "opp", "forgot", "SSS", "Vibing++"):
        if by.get(g):
            part2(g, by[g])
    P("\n\nPART 3")
    part3(recs)
    P("\n\nPART 4: feeder pearls eaten by the enemy, by how near an enemy head is when the feeder dies (from round 150)")
    for g in ("meow live", "meow test", "opp", "forgot", "SSS", "Vibing++"):
        if by.get(g):
            part4(g, by[g])


if __name__ == "__main__":
    main()
