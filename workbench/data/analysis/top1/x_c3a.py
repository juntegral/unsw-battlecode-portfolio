#!/usr/bin/env python3
"""Candidate 3 ("no leader before its time"): my recount. Reads x_out/c34/ (x_c34.py) and x_out/c1/ (timeline).
Output: x_out/c3a.txt

1. A free pearl on the next cell taken or not (dragon 2-4, not the queen, no enemy head in view, a way on), by map
   class, team and round band; in 10-round blocks around our two switch rounds; by the distance to the nearest longer
   own dragon and by that dragon's length; by the dragon's own length.
2. The same inside our wins and our losses, and by economy band, to see whether the fall is the switch or the state.
3. Splits per dragon-turn by length class, around the switch.
4. Units, total length, longest dragon at rounds 100-450 by map class and team; growth 150 -> 300.
5. Natural pearls eaten per game per 50 rounds.
"""
from collections import Counter, defaultdict

import x_load as X

out = open("x_out/c3a.txt", "w")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


g34 = {g["gid"]: g for g in X.games("c34") if g["d"]}
g1 = {g["gid"]: g for g in X.games("c1") if g["d"]}
gs = [g for g in g34.values() if X.is_csv(g)]
P("games with c34 data:", len(g34))


def big(g):
    return g["cells"] > 1200


cols = defaultdict(list)
for g in gs:
    for side in "AB":
        team = g[side]
        if not X.in_study(g, side):
            continue
        if team == X.ME:
            b = X.build(g)
            cols["meow all"].append((g, side))
            cols["meow live" if b == "live" else ("meow tc30" if b == "tc30" else "meow other test")].append((g, side))
            cols["our opponents"].append((g, X.other(side)))
        if team in X.TOP3:
            cols[X.NAMES[team]].append((g, side))
            cols["top three"].append((g, side))
order = ["meow live", "meow tc30", "meow other test", "meow all", "our opponents", "Vibing++", "SSS", "forgot", "top three"]


def pearl_rows(g, side):
    for key, v in g["d"]["pearl"]:
        if key[0] == side:
            yield key, v   # (side, rb, L, dbucket, leaderclass, taken), count


def rate(sel, f):
    n = t = 0
    for g, side in sel:
        for key, v in pearl_rows(g, side):
            if f(key):
                n += v
                t += v * key[5]
    return t, n


for cls_name, cls in (("MAPS OVER 1,200 CELLS (our switch: round 150)", True), ("MAPS OF 1,200 CELLS OR FEWER (our switch: round 300)", False)):
    P("\n" + "=" * 20, cls_name, "=" * 20)
    sel = {k: [(g, s) for g, s in cols[k] if big(g) == cls] for k in order}
    P("games:", {k: len(sel[k]) for k in order})
    P("\n-- 1a. free pearl on the next cell eaten, by round band")
    P("%-34s" % "" + "".join("%-18s" % k for k in order))
    for lab, lo, hi in (("rounds 0-149", 0, 15), ("rounds 150-299", 15, 30), ("rounds 300-399", 30, 40), ("rounds 400+", 40, 99)):
        P("%-34s" % lab + "".join("%-18s" % ("%s of %d" % (X.pct(*rate(sel[k], lambda key: lo <= key[1] < hi)), rate(sel[k], lambda key: lo <= key[1] < hi)[1])) for k in order))
    P("\n-- 1b. in 10-round blocks around the switch")
    blocks = range(10, 22) if cls else range(25, 37)
    P("%-34s" % "" + "".join("%-18s" % k for k in order))
    for rb in blocks:
        P("%-34s" % ("rounds %d-%d" % (rb * 10, rb * 10 + 9)) + "".join("%-18s" % ("%s of %d" % (X.pct(*rate(sel[k], lambda key: key[1] == rb)), rate(sel[k], lambda key: key[1] == rb)[1])) for k in order))
    lo, hi = (15, 40) if cls else (30, 40)
    blo, bhi = (0, 15) if cls else (0, 30)
    P("\n-- 1c. after the switch (rounds %d-%d), by the distance from the pearl to the nearest LONGER own dragon" % (lo * 10, hi * 10 - 1))
    P("%-34s" % "" + "".join("%-18s" % k for k in order))
    for lab, db in (("0-3 cells", 0), ("4-6", 1), ("7-9", 2), ("10-12", 3), ("13-16", 4), ("17+", 5), ("no longer own dragon on the board", 9)):
        P("%-34s" % lab + "".join("%-18s" % ("%s of %d" % (X.pct(*rate(sel[k], lambda key: lo <= key[1] < hi and key[3] == db)), rate(sel[k], lambda key: lo <= key[1] < hi and key[3] == db)[1])) for k in order))
    P("   the same BEFORE the switch (rounds %d-%d)" % (blo * 10, bhi * 10 - 1))
    for lab, db in (("0-3 cells", 0), ("4-6", 1), ("7-9", 2), ("10-12", 3), ("13-16", 4), ("17+", 5), ("no longer own dragon on the board", 9)):
        P("%-34s" % lab + "".join("%-18s" % ("%s of %d" % (X.pct(*rate(sel[k], lambda key: blo <= key[1] < bhi and key[3] == db)), rate(sel[k], lambda key: blo <= key[1] < bhi and key[3] == db)[1])) for k in order))
    P("\n-- 1d. after the switch, a longer own dragon within 9 cells: by that dragon's length")
    for lab, lc in (("it is 3-4 long", "3-4"), ("5-9", "5-9"), ("10+", "10+")):
        P("%-34s" % lab + "".join("%-18s" % ("%s of %d" % (X.pct(*rate(sel[k], lambda key: lo <= key[1] < hi and key[3] <= 2 and key[4] == lc)), rate(sel[k], lambda key: lo <= key[1] < hi and key[3] <= 2 and key[4] == lc)[1])) for k in order))
    P("\n-- 1e. by the dragon's own length: before the switch / after")
    for L in (2, 3, 4):
        P("%-34s" % ("own length %d" % L) + "".join("%-18s" % ("%s / %s" % (X.pct(*rate(sel[k], lambda key: blo <= key[1] < bhi and key[2] == L)), X.pct(*rate(sel[k], lambda key: lo <= key[1] < hi and key[2] == L)))) for k in order))

    P("\n-- 2. Is it the switch or the state of the game? Our live bot after the switch, by result and by economy band at the switch round")
    R = 150 if cls else 300
    for lab, pred in (("games we won", lambda g, s: X.won(g, s)), ("games we lost", lambda g, s: not X.won(g, s))):
        s2 = [(g, s) for g, s in sel["meow live"] if pred(g, s)]
        b = rate(s2, lambda key: blo <= key[1] < bhi)
        a = rate(s2, lambda key: lo <= key[1] < hi)
        P("   %-22s games %-4d before %s of %d, after %s of %d" % (lab, len(s2), X.pct(*b), b[1], X.pct(*a), a[1]))
    for bnd in range(4):
        s2 = []
        for g, s in sel["meow live"]:
            d1 = g1[g["gid"]]["d"]
            o, e = X.stats_at(d1, R, s), X.stats_at(d1, R, X.other(s))
            if o and e and e[1] and X.band(o[1] / e[1]) == bnd:
                s2.append((g, s))
        b = rate(s2, lambda key: blo <= key[1] < bhi)
        a = rate(s2, lambda key: lo <= key[1] < hi)
        P("   band %-7s at r%d   games %-4d before %s of %d, after %s of %d" % (X.BAND_NAMES[bnd], R, len(s2), X.pct(*b), b[1], X.pct(*a), a[1]))

    P("\n-- 3. Splits per 100 dragon-turns by length class (non-queens), per 50 rounds")
    for lc in ("4", "5-9", "10+"):
        P("   parent length %s" % lc)
        P("%-34s" % "" + "".join("%-18s" % k for k in order))
        for r0 in range(0, 450, 50):
            line = "%-34s" % ("rounds %d-%d" % (r0, r0 + 49))
            for k in order:
                sp = tn = 0
                for g, side in sel[k]:
                    for key, v in g["d"]["splits"]:
                        if key[0] == side and key[2] == lc and r0 <= key[1] * 10 < r0 + 50:
                            sp += v
                    for key, v in g["d"]["turns"]:
                        if key[0] == side and key[2] == lc and r0 <= key[1] * 10 < r0 + 50:
                            tn += v
                line += "%-18s" % ("%.1f (%.1f/game)" % (100.0 * sp / max(1, tn), sp / max(1, len(sel[k]))))
            P(line)

    P("\n-- 4. Units / total length / longest dragon (means over games that reach the round)")
    P("%-12s" % "" + "".join("%-22s" % k for k in order))
    table = {}
    for Rr in (100, 150, 200, 250, 300, 350, 400, 450):
        line = "%-12s" % ("round %d" % Rr)
        for k in order:
            u = t = lg = n = 0
            for g, side in sel[k]:
                st = X.stats_at(g1[g["gid"]]["d"], Rr, side)
                if st is None:
                    continue
                n += 1
                u += st[0]
                t += st[1]
                lg += st[2]
            table[(k, Rr)] = (u / max(1, n), t / max(1, n), lg / max(1, n), n)
            line += "%-22s" % ("%.1f / %.0f / %.1f (%d)" % (u / max(1, n), t / max(1, n), lg / max(1, n), n))
        P(line)
    P("   growth of total length 150 -> 300 / of the longest dragon: " + "; ".join(
        "%s %+.0f%% / %+.1f" % (k, 100 * (table[(k, 300)][1] / max(1, table[(k, 150)][1]) - 1), table[(k, 300)][2] - table[(k, 150)][2]) for k in order))

    P("\n-- 5. Pearls eaten per game per 50 rounds: natural by dragons that were 2-4 / natural by 5+ / corpse pearls (all)")
    P("%-16s" % "" + "".join("%-22s" % k for k in order))
    for r0 in range(0, 500, 50):
        line = "%-16s" % ("rounds %d-%d" % (r0, r0 + 49))
        for k in order:
            a = b5 = c = 0
            for g, side in sel[k]:
                for key, v in g["d"]["eaten"]:
                    if key[0] != side or not (r0 <= key[1] * 10 < r0 + 50):
                        continue
                    if key[2] == "nat" and key[3] == "2-4":
                        a += v
                    elif key[2] == "nat" and key[3] == "5+":
                        b5 += v
                    elif key[2] == "corpse":
                        c += v
            n = max(1, len(sel[k]))
            line += "%-22s" % ("%.0f / %.0f / %.0f" % (a / n, b5 / n, c / n))
        P(line)
out.close()
