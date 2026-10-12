#!/usr/bin/env python3
"""Question (c): who the leader is and whether it lasts. Round-500 games with both queens dead.

Per group and map class:
  1. Is the team's longest dragon at round 250 / 300 / 350 / 400 / 450 the same dragon (same id) as the longest at the end?
     Is it on the final leader's lineage (the same dragon or an ancestor through splits)?
  2. Leader losses: deaths of the team's longest dragon when it was 15+ / 25+ long, by kind (rammed by an enemy and that
     enemy's length, it rammed, boxed in, by choice), per game and per 1,000 rounds in which the team had such a leader;
     what the team's longest was 25 and 50 rounds later.
  3. Leader splits: splits of the team's longest dragon (15+) by what the head keeps (2-3 = the "boxed" split that hands the
     length to a new id; a shed of 2 from the tail; other), per game.
  4. Where the leader lives at rounds 300 / 350 / 400 / 450: distance to the nearest enemy head, open or closed ground,
     distance from its own queen's start, whether portals separate it from the enemy start, own heads near it; how much it
     moves and eats by itself per 25 rounds.
  5. One leader or several: second and third longest relative to the longest; dragons of 15+.
Reads e_out/w. Output: e_out/c_leader.txt
"""
from collections import Counter, defaultdict

import e_data as D

P = D.Out("c_leader.txt")
CHECK = (250, 300, 350, 400, 450)


def block(recs, title):
    n = len(recs)
    if not n:
        return
    DI = {k: i for i, k in enumerate(recs[0].d["dcol"])}
    P("\n--- %s: %d games, won %d" % (title, n, sum(r.won for r in recs)))
    # 1. identity
    for r0 in CHECK:
        same = lin = big = 0
        for r in recs:
            t = r.tl(r0)
            fid = r.s["lin"]["id"]
            i = r0 // 5
            same += t[4] == fid
            lin += r.s["lin"]["ids"][i] == t[4]
        P("    longest at round %d: the same id as the final longest in %s; the same dragon or its ancestor (lineage) in %s; median length then %s" % (
            r0, D.frac(same, n), D.frac(lin, n), D.med([r.tl(r0)[3] for r in recs])))
    # 2. leader losses
    for T in (15, 25):
        kinds = Counter()
        klen = []
        after = []
        rounds_with = 0
        early = Counter()
        for r in recs:
            tl = r.s["tl"]
            rounds_with += 5 * sum(1 for row in tl if row[3] >= T)
            for x in r.s["deaths"]:
                if x[DI["rank"]] == 1 and x[2] >= T:
                    c = x[DI["cls"]]
                    kinds[("rammed by an enemy", "it rammed", "by choice", "boxed in", "rammed by own")[c]] += 1
                    early["before 300" if x[0] < 300 else "300-399" if x[0] < 400 else "400+"] += 1
                    if c == 0:
                        klen.append(x[DI["klen"]])
                    i = x[0] // 5
                    a = tl[min(len(tl) - 1, i + 6)][3]
                    after.append((x[2], a))
        tot = sum(kinds.values())
        P("    the team's longest dragon died when %d+ long: %d times in %d games (%.2f a game; %.1f per 1,000 rounds with such a leader); %s; by round: %s" % (
            T, tot, n, tot / n, 1000.0 * tot / max(1, rounds_with), dict(kinds), dict(early)))
        if klen:
            c = Counter("2-4" if k <= 4 else "5-9" if k <= 9 else "10+" for k in klen)
            P("        length of the enemy that rammed it: %s" % dict(c))
        if after:
            P("        median length lost %s; the team's longest 25-30 rounds later: median %s" % (D.med([a for a, b in after]), D.med([b for a, b in after])))
    # 3. leader splits
    kinds = Counter()
    for r in recs:
        for x in r.s["splits"]:
            if x[7] and x[3] >= 15:
                keep, child = x[4], x[5]
                k = "head keeps 2-3, the rest goes to a new id" if keep <= 3 else "sheds 2-3 from the tail" if child <= 3 else "other"
                kinds[k + (" (no free cell)" if x[6] == 0 else " (a free cell)")] += 1
    P("    splits of the team's longest dragon when 15+: " + ", ".join("%s: %.2f a game" % (k, v / n) for k, v in kinds.most_common()))
    hs = [sum(1 for h in r.s["lin"]["hand"] if h[0] >= 300 and h[3] >= 15) for r in recs]
    P("    handovers of the final lineage from round 300 with a parent of 15+: %.2f a game; none in %s of the games; 3 or more in %s" % (
        sum(hs) / n, D.pct(sum(1 for h in hs if h == 0), n), D.pct(sum(1 for h in hs if h >= 3), n)))
    # 4. where the leader lives
    P("    the leader at round:                         " + "".join("%8d" % r0 for r0 in (200, 250, 300, 350, 400, 450, 475)))
    rows = defaultdict(lambda: defaultdict(list))
    for r in recs:
        lead = {row[0]: row for row in r.s["lead"]}
        prev = None
        for r0 in (175, 200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475):
            row = lead.get(r0)
            if row is None:
                prev = None
                continue
            rows["length"][r0].append(row[2])
            rows["Manhattan distance to the nearest enemy head"][r0].append(row[6])
            rows["an enemy head within 12 path steps, %"][r0].append(100.0 if row[8] >= 0 else 0.0)
            rows["an enemy head within 6 path steps, %"][r0].append(100.0 if 0 <= row[8] <= 6 else 0.0)
            rows["cells within 4 steps of its head (41 = open)"][r0].append(row[5])
            rows["Manhattan distance to its own queen's start"][r0].append(row[11])
            rows["portals separate it from the enemy start, %"][r0].append(0.0 if row[12] else 100.0)
            rows["own heads within 6 path steps"][r0].append(row[10])
            rows["own heads within 15 cells"][r0].append(row[21])
            rows["their summed length"][r0].append(row[22])
            rows["... as % of the rest of the team's length"][r0].append(100.0 * row[22] / max(1, r.tl(r0)[2] - row[2]))
            if row[27] >= 0:
                rows["path steps from the team's heads to it: median"][r0].append(row[27])
                rows["path steps from the team's heads to it: 80th pct"][r0].append(row[28])
            rows["own dragons over half its length: number"][r0].append(row[25])
            rows["own dragons over half its length: their length"][r0].append(row[26])
            if prev is not None and prev[1] == row[1]:
                rows["steps it took in the last 25 rounds (same id)"][r0].append(row[14] - prev[14])
                rows["segments paid in the last 25 rounds"][r0].append(row[15] - prev[15])
                rows["natural pearls it ate in the last 25 rounds"][r0].append(row[16] - prev[16])
                rows["corpse pearls it ate in the last 25 rounds"][r0].append(row[17] - prev[17])
            prev = row
    for name in ("length", "Manhattan distance to the nearest enemy head", "an enemy head within 12 path steps, %", "an enemy head within 6 path steps, %",
                 "cells within 4 steps of its head (41 = open)", "Manhattan distance to its own queen's start", "portals separate it from the enemy start, %",
                 "own heads within 6 path steps", "own heads within 15 cells", "their summed length", "... as % of the rest of the team's length",
                 "path steps from the team's heads to it: median", "path steps from the team's heads to it: 80th pct",
                 "own dragons over half its length: number", "own dragons over half its length: their length",
                 "steps it took in the last 25 rounds (same id)", "segments paid in the last 25 rounds", "natural pearls it ate in the last 25 rounds",
                 "corpse pearls it ate in the last 25 rounds"):
        f = D.mean if name.endswith("%") or "last 25" in name else D.med
        P("      %-46s" % name + "".join("%8s" % f(rows[name][r0]) for r0 in (200, 250, 300, 350, 400, 450, 475)))
    # 5. one leader or several
    for r0 in (400, 450):
        P("    round %d: second / longest median %s, third / longest %s; dragons of 15+: mean %s" % (
            r0, D.med([r.tl(r0)[5] / max(1, r.tl(r0)[3]) for r in recs], 2), D.med([r.tl(r0)[6] / max(1, r.tl(r0)[3]) for r in recs], 2),
            D.mean([r.tl(r0)[9] for r in recs])))
    fin = [r.s["final"] for r in recs]
    P("    end: longest median %s, second %s, third %s; second / longest median %s; longest as share of total: median %s%%; units median %s" % (
        D.med([f["top"][0][0] for f in fin]), D.med([f["top"][1][0] if len(f["top"]) > 1 else 0 for f in fin]),
        D.med([f["top"][2][0] if len(f["top"]) > 2 else 0 for f in fin]),
        D.med([(f["top"][1][0] if len(f["top"]) > 1 else 0) / max(1, f["top"][0][0]) for f in fin], 2),
        D.med([100.0 * f["top"][0][0] / max(1, f["total"]) for f in fin]), D.med([f["units"] for f in fin])))
    # the "unconverted" what-if
    flips = [r for r in recs if not r.won and r.s["final"]["top"][0][0] + (r.s["final"]["total"] - r.s["final"]["top"][0][0]) / 2 > r.o["final"]["top"][0][0]]
    flips38 = [r for r in recs if not r.won and r.s["final"]["top"][0][0] + 0.38 * (r.s["final"]["total"] - r.s["final"]["top"][0][0]) > r.o["final"]["top"][0][0]]
    lost = [r for r in recs if not r.won]
    P("    losses in which the final longest plus HALF of the rest of the own final length beats the enemy's final longest: %s; with 0.38 of the rest: %s" % (
        D.frac(len(flips), len(lost)), D.frac(len(flips38), len(lost))))
    wins_risk = [r for r in recs if r.won and r.o["final"]["top"][0][0] + (r.o["final"]["total"] - r.o["final"]["top"][0][0]) / 2 > r.s["final"]["top"][0][0]]
    P("    wins in which the ENEMY's final longest plus half of the rest of its length would have beaten ours: %s" % D.frac(len(wins_risk), len(recs) - len(lost)))


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
