#!/usr/bin/env python3
"""Question (d): our two switches as natural experiments.

Part 1, the leader zone. Our bot: from `grow_round` on (round 150 on maps over 1,200 cells, 300 otherwise) a small dragon
does not take a pearl within 9 cells of the leader it knows of. Counted here on every turn of a non-queen dragon of 2-4
that moves, has no enemy head in its 7x7 view and has a pearl on a free next cell with a further free neighbour:
  - how often the pearl is taken, per 50 rounds, by where the pearl lies (within 9 cells of the team's true leader of 5+ /
    farther / no such leader) and, for meow, by what the dragon itself believed (decoded from its own sonar ping of that
    turn: every such pearl within 9 cells of its believed leader / not / it believes it is the leader itself);
  - what became of every pearl left lying on such a turn: eaten by the leader of the time, by another own dragon, by the
    enemy, or by nobody within 30 rounds; how long it lay.
Part 2, feeding. Our bot's feeder deaths are its `noaction` deaths (the bot returns without an order). For each of our
games: the round of the first three such deaths within 15 rounds = the start of feeding; games grouped by that start
(before 300 / 300-399 / 400 or later / never) inside the same band of total length at round 300: the leader's curve and
the result. And which mechanism builds our leader round for round: natural pearls against feeder pearls.
Reads e_out/w3. Output: e_out/d_switch.txt
"""
from collections import Counter, defaultdict

import e_data as D
import e_lib as E

P = D.Out("d_switch.txt")
BINS = list(range(2, 10))


def zone_part(recs, title, me):
    n = len(recs)
    if not n:
        return
    P("\n--- %s: %d games (all games of the group on these maps, any ending)" % (title, n))
    P("    %-66s" % "rounds" + "".join("%9s" % ("%d-%d" % (b * 50, b * 50 + 49)) for b in BINS))
    adj = defaultdict(lambda: [0, 0])
    adjz = defaultdict(lambda: [0, 0])
    for r in recs:
        for k, v in r.s["adj"].items():
            b10, near = (int(x) for x in k.split("|"))
            a = adj[(b10 // 5, near)]
            a[0] += v[0]
            a[1] += v[1]
            a = adj[(b10 // 5, 9)]
            a[0] += v[0]
            a[1] += v[1]
        if me:
            for k, v in r.s.get("adjz", {}).items():
                b10, flag = (int(x) for x in k.split("|"))
                a = adjz[(b10 // 5, flag)]
                a[0] += v[0]
                a[1] += v[1]

    def rate(d, key):
        return "".join("%9s" % (("%s/%d" % (D.pct(d[(b, key)][1], d[(b, key)][0]), d[(b, key)][0])) if d[(b, key)][0] else "-") for b in BINS)

    P("    %-66s" % "pearl taken / such turns: all" + rate(adj, 9))
    P("    %-66s" % "  the pearl is within 9 cells of the true leader (5+ long)" + rate(adj, 0))
    P("    %-66s" % "  farther from it" + rate(adj, 1))
    P("    %-66s" % "  no own leader of 5+ (or the dragon is the leader)" + rate(adj, 2))
    if me:
        P("    %-66s" % "  by belief: every such pearl inside the believed leader's zone" + rate(adjz, 1))
        P("    %-66s" % "  by belief: a pearl outside the believed zone" + rate(adjz, 0))
        P("    %-66s" % "  by belief: the dragon believes it is the leader itself" + rate(adjz, 2))
        P("    %-66s" % "  belief unknown (no ping that turn)" + rate(adjz, -1))
    # declined pearls
    for lab, sel in (("pearls left lying (all)", lambda z: True),
                     ("... within 9 cells of the true leader (5+)", lambda z: 0 <= z[5] <= 9 and z[6] >= 5),
                     ("... inside the believed leader's zone (meow)", lambda z: z[10] == 1)):
        if "believed" in lab and not me:
            continue
        cnt = Counter()
        fate = defaultdict(Counter)
        delay = defaultdict(list)
        for r in recs:
            for z in r.s["zone"]:
                if not sel(z):
                    continue
                b = z[0] // 50
                cnt[b] += 1
                f, dl = z[12], z[13]
                if f == 3 or dl > 30:
                    fate[b]["nobody within 30 rounds"] += 1
                elif f == 2:
                    fate[b]["the enemy"] += 1
                elif f == 0 or z[16] == 1:
                    fate[b]["the leader"] += 1
                elif z[14] >= 8:
                    fate[b]["another own dragon of 8+"] += 1
                else:
                    fate[b]["another own dragon under 8"] += 1
                if f != 3:
                    delay[b].append(dl)
        P("    %-66s" % ("%s: per game" % lab) + "".join("%9.1f" % (cnt[b] / n) for b in BINS))
        for k in ("the leader", "another own dragon of 8+", "another own dragon under 8", "the enemy", "nobody within 30 rounds"):
            P("    %-66s" % ("      eaten in the end by %s" % k) + "".join("%9s" % D.pct(fate[b][k], cnt[b]) for b in BINS))
        P("    %-66s" % "      rounds it lay before it was eaten (median)" + "".join("%9s" % D.med(delay[b]) for b in BINS))
    P("    %-66s" % "natural pearls eaten per game: the leader of the time" + "".join("%9.1f" % (sum(r.s["eats"].get("L|%d|0" % b, 0) for r in recs) / n) for b in BINS))
    P("    %-66s" % "natural pearls eaten per game: the whole team" + "".join("%9.1f" % (sum(r.s["eats"].get("T|%d|0" % b, 0) for r in recs) / n) for b in BINS))
    P("    %-66s" % "natural pearls eaten per game: the ENEMY" + "".join("%9.1f" % (sum(r.o["eats"].get("T|%d|0" % b, 0) for r in recs) / n) for b in BINS))
    P("    %-66s" % "splits per game" + "".join("%9.1f" % (sum(r.s["nsplit"].get(str(b), 0) for r in recs) / n) for b in BINS))

    def tlmed(col, own=True):
        out = ""
        for b in BINS:
            v = [r.tl(b * 50, own)[col] for r in recs if r.tl(b * 50, own)]
            out += "%9s" % D.med(v)
        return out

    P("    %-66s" % "at the start of the block: games still running" + "".join("%9d" % sum(1 for r in recs if r.tl(b * 50)) for b in BINS))
    P("    %-66s" % "  units (median)" + tlmed(1))
    P("    %-66s" % "  total length" + tlmed(2))
    P("    %-66s" % "  longest" + tlmed(3))
    P("    %-66s" % "  ENEMY units" + tlmed(1, False))
    P("    %-66s" % "  ENEMY total length" + tlmed(2, False))
    P("    %-66s" % "  ENEMY longest" + tlmed(3, False))


def feed_start(r, DI, need=3, span=15):
    rs = sorted(x[0] for x in r.s["deaths"] if x[DI["reason"]] == 4 and x[DI["akind"]] == 2 and not x[DI["tle"]])
    for i in range(len(rs) - need + 1):
        if rs[i + need - 1] - rs[i] <= span:
            return rs[i]
    return None


def feed_part(recs, title):
    recs = [r for r in recs if r.tl(300) is not None]
    if not recs:
        return
    DI = {k: i for i, k in enumerate(recs[0].d["dcol"])}
    P("\n--- %s: %d games that reach round 300" % (title, len(recs)))
    rows = [(r, feed_start(r, DI)) for r in recs]
    h = Counter((st // 25 * 25) if st is not None else "never" for r, st in rows)
    P("    start of feeding (first of three `noaction` deaths within 15 rounds) by 25-round block: " + ", ".join(
        "%s: %d" % (k, h[k]) for k in sorted(h, key=lambda z: (z == "never", z if z != "never" else 0))))
    n56 = [(r, st) for r, st in rows if r.tl(200)[1] >= 56]
    P("    games with 56+ units at round 200: %d; their start round: %s" % (len(n56), sorted(st for r, st in n56 if st is not None)[:60]))
    qal = [(r, st) for r, st in rows if r.tl(300)[7] > 0]
    P("    games with our queen alive at round 300: %d; their start round: %s" % (len(qal), sorted(st for r, st in qal if st is not None)[:60]))

    def cls(st):
        return "never" if st is None else "before 300" if st < 300 else "300-399" if st < 400 else "400 or later"

    for band, lo, hi in (("total length at round 300 under 0.67 of the enemy's", 0, 0.67), ("0.67 to 1", 0.67, 1.0), ("1 or more", 1.0, 99)):
        P("    -- %s" % band)
        P("       %-14s %5s %4s | %-9s %-7s | own longest at 300 / 350 / 400 / 450 / end | enemy's | units at 300 / 400 / end | total at 300 / 400 / end" % (
            "feeding starts", "games", "won", "both dead", "won"))
        for c in ("before 300", "300-399", "400 or later", "never"):
            v = [r for r, st in rows if cls(st) == c and r.ratio(300) is not None and lo <= r.ratio(300) < hi]
            if not v:
                continue
            bd = [r for r in v if r.bd]
            full = [r for r in v if r.r500]

            def m(fn, src=full):
                return D.med([fn(r) for r in src])

            P("       %-14s %5d %4d | %-9d %-7d | %s / %s / %s / %s / %s | %s / %s / %s / %s / %s | %s / %s / %s | %s / %s / %s   (medians over the %d round-500 games)" % (
                c, len(v), sum(r.won for r in v), len(bd), sum(r.won for r in bd),
                m(lambda r: r.tl(300)[3]), m(lambda r: r.tl(350)[3]), m(lambda r: r.tl(400)[3]), m(lambda r: r.tl(450)[3]), m(lambda r: r.s["final"]["top"][0][0]),
                m(lambda r: r.tl(300, False)[3]), m(lambda r: r.tl(350, False)[3]), m(lambda r: r.tl(400, False)[3]), m(lambda r: r.tl(450, False)[3]),
                m(lambda r: r.o["final"]["top"][0][0]),
                m(lambda r: r.tl(300)[1]), m(lambda r: r.tl(400)[1]), m(lambda r: r.s["final"]["units"]),
                m(lambda r: r.tl(300)[2]), m(lambda r: r.tl(400)[2]), m(lambda r: r.s["final"]["total"]), len(full)))
    # which mechanism builds the leader
    full = [r for r in recs if r.bd]
    if full:
        n = len(full)
        P("    which mechanism builds the leader, per game, round-500 games with both queens dead (%d):" % n)
        P("       %-56s" % "rounds" + "".join("%9s" % ("%d-%d" % (b * 50, b * 50 + 49)) for b in BINS))
        for lab, role, codes in (("lineage: natural pearls", "N", (0,)), ("lineage: pearls of own dragons dead by choice", "N", (1,)),
                                 ("lineage: pearls of own dragons boxed in or rammed", "N", (2, 3)), ("lineage: pearls of enemy corpses", "N", (4, 5, 6)),
                                 ("leader of the time: natural pearls", "L", (0,)), ("leader of the time: pearls of own dead by choice", "L", (1,))):
            P("       %-56s" % lab + "".join("%9.1f" % (sum(sum(r.s["eats"].get("%s|%d|%d" % (role, b, c), 0) for c in codes) for r in full) / n) for b in BINS))
        P("       %-56s" % "our `noaction` deaths (feeders): number" + "".join(
            "%9.1f" % (sum(1 for r in full for x in r.s["deaths"] if x[DI["reason"]] == 4 and x[DI["akind"]] == 2 and x[0] // 50 == b) / n) for b in BINS))
        P("       %-56s" % "... their summed length" + "".join(
            "%9.1f" % (sum(x[2] for r in full for x in r.s["deaths"] if x[DI["reason"]] == 4 and x[DI["akind"]] == 2 and x[0] // 50 == b) / n) for b in BINS))


def main():
    recs = D.rows()
    by = defaultdict(list)
    for r in recs:
        for g in D.groups(r):
            by[g].append(r)
    P("PART 1: THE LEADER ZONE")
    for cls, name in ((False, "maps of 1,200 cells or fewer (our switch: round 300)"), (True, "maps over 1,200 cells (our switch: round 150)")):
        P("\n==================== %s ====================" % name)
        for g in ("meow live", "meow test", "opp", "forgot", "SSS", "Vibing++"):
            zone_part([r for r in by.get(g, []) if r.big == cls], "%s | %s" % (g, name), g.startswith("meow"))
    P("\n\nPART 2: FEEDING")
    for cls, name in ((False, "maps of 1,200 cells or fewer"), (True, "maps over 1,200 cells")):
        for g in ("meow live", "meow test"):
            feed_part([r for r in by.get(g, []) if r.big == cls], "%s | %s" % (g, name))


if __name__ == "__main__":
    main()
