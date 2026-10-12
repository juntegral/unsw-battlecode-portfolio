#!/usr/bin/env python3
"""Candidate 4 ("do not give way at contact"): my recount. Reads x_out/c34/ (x_c34.py) and x_out/c1/ (timeline).
Output: x_out/c4a.txt

1. Ram chances on small enemy heads (both dragons 4 or shorter, not queens) taken, by map class, team, head count
   ("not outnumbered" = other own heads in view >= enemy heads in view), relative length and distance (next cell /
   2-3 steps).
2. Rams started per game by class, and the swing per ram: (pearls of the two corpses eaten by the starter's team
   minus its dragon's length) minus (the same for the other team).
3. The same for our wins against our losses, and for the top three.
4. The trade-on-contact build (tc30) against the live bot on maps over 1,200 cells: economy and results.
"""
from collections import Counter, defaultdict

import x_load as X

out = open("x_out/c4a.txt", "w")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


g34 = {g["gid"]: g for g in X.games("c34") if g["d"]}
g1 = {g["gid"]: g for g in X.games("c1") if g["d"]}
gs = [g for g in g34.values() if X.is_csv(g)]


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
            if b == "live":
                cols["opp of live"].append((g, X.other(side)))
            if b == "tc30":
                cols["opp of tc30"].append((g, X.other(side)))
        if team in X.TOP3:
            cols[X.NAMES[team]].append((g, side))
            cols["top three"].append((g, side))
order = ["meow live", "meow tc30", "our opponents", "Vibing++", "SSS", "forgot", "top three"]
RELS = ("longer", "same", "shorter")


def chances(sel, f):
    n = t = 0
    for g, side in sel:
        for key, v in g["d"]["chance"]:
            # (side, phase, notout, rel, adj, taken)
            if key[0] == side and f(key):
                n += v
                t += v * key[5]
    return t, n


def rams(sel, f):
    """Rams started by `side` between two small non-queens: count, sum starter length, victim length, pearls eaten by starter's team / the other."""
    c = Counter()
    for g, side in sel:
        es = X.other(side)
        for r in g["d"]["rams"]:
            if r["side"] != side or not f(r):
                continue
            c["n"] += 1
            c["sL"] += r["sL0"]
            c["vL"] += r["vL"]
            c["eat_s"] += r.get("eat_" + side, 0)
            c["eat_o"] += r.get("eat_" + es, 0)
    return c


def swing(c):
    if not c["n"]:
        return None
    return ((c["eat_s"] - c["sL"]) - (c["eat_o"] - c["vL"])) / c["n"]


for cls_name, cls in (("MAPS OVER 1,200 CELLS", True), ("MAPS OF 1,200 CELLS OR FEWER", False)):
    P("\n" + "=" * 20, cls_name, "=" * 20)
    sel = {k: [(g, s) for g, s in cols[k] if big(g) == cls] for k in list(cols)}
    P("games:", {k: len(sel[k]) for k in order})
    P("\n-- 1. Share of chances that end in its ram: enemy head on the next cell / 2-3 free steps away  (all rounds)")
    P("%-44s" % "" + "".join("%-20s" % k for k in order))
    for notout, nlab in ((1, "not outnumbered"), (0, "alone or outnumbered")):
        for rel in RELS:
            line = "%-44s" % ("%s, enemy %s" % (nlab, rel))
            for k in order:
                a = chances(sel[k], lambda key: key[2] == notout and key[3] == rel and key[4] == 1)
                b = chances(sel[k], lambda key: key[2] == notout and key[3] == rel and key[4] == 2)
                line += "%-20s" % ("%s / %s" % (X.pct(*a), X.pct(*b)))
            P(line)
    P("   number of chances per game (next cell + 2-3 steps), not outnumbered / alone or outnumbered:")
    P("%-44s" % "" + "".join("%-20s" % ("%.0f / %.0f" % (chances(sel[k], lambda key: key[2] == 1)[1] / max(1, len(sel[k])),
                                                          chances(sel[k], lambda key: key[2] == 0)[1] / max(1, len(sel[k])))) for k in order))
    P("   all chances, share taken:")
    P("%-44s" % "" + "".join("%-20s" % X.frac(*chances(sel[k], lambda key: True)) for k in order))
    P("   the same in rounds 0-149 only (next cell, enemy same length, not outnumbered / alone):")
    P("%-44s" % "" + "".join("%-20s" % ("%s / %s" % (
        X.pct(*chances(sel[k], lambda key: key[1] == 0 and key[2] == 1 and key[3] == "same" and key[4] == 1)),
        X.pct(*chances(sel[k], lambda key: key[1] == 0 and key[2] == 0 and key[3] == "same" and key[4] == 1)))) for k in order))

    P("\n-- 2. Rams this side starts (both dragons 4 or shorter): per game, and swing in segments per ram")
    P("%-44s" % "" + "".join("%-20s" % k for k in order))
    for notout, nlab in ((1, "not outnumbered"), (0, "alone or outnumbered"), (None, "head count unknown (no chance record)")):
        for rel in RELS:
            line = "%-44s" % ("%s, victim %s" % (nlab, rel))
            for k in order:
                c = rams(sel[k], lambda r: r.get("notout") == notout and r["rel"] == rel)
                sw = swing(c)
                line += "%-20s" % ("%.1f/g  %s" % (c["n"] / max(1, len(sel[k])), ("%+.2f" % sw) if sw is not None else "-"))
            P(line)
    line = "%-44s" % "all rams it starts: per game x swing = segments"
    for k in order:
        c = rams(sel[k], lambda r: True)
        sw = swing(c) or 0.0
        n = c["n"] / max(1, len(sel[k]))
        line += "%-20s" % ("%.1f x %+.2f = %+.0f" % (n, sw, n * sw))
    P(line)
    line = "%-44s" % "share of both corpses' pearls its team eats"
    for k in order:
        c = rams(sel[k], lambda r: True)
        line += "%-20s" % X.pct(c["eat_s"], c["eat_s"] + c["eat_o"])
    P(line)
    line = "%-44s" % "... not outnumbered / alone or outnumbered"
    for k in order:
        c1 = rams(sel[k], lambda r: r.get("notout") == 1)
        c0 = rams(sel[k], lambda r: r.get("notout") == 0)
        line += "%-20s" % ("%s / %s" % (X.pct(c1["eat_s"], c1["eat_s"] + c1["eat_o"]), X.pct(c0["eat_s"], c0["eat_s"] + c0["eat_o"])))
    P(line)

    P("\n-- 3. Rams started per game in this side's wins / losses (all classes), and the swing")
    for k in order:
        w = [(g, s) for g, s in sel[k] if X.won(g, s)]
        l = [(g, s) for g, s in sel[k] if not X.won(g, s)]
        cw, cl = rams(w, lambda r: True), rams(l, lambda r: True)
        P("   %-16s wins %-4d %.1f rams a game, swing %s | losses %-4d %.1f a game, swing %s" % (
            k, len(w), cw["n"] / max(1, len(w)), ("%+.2f" % swing(cw)) if cw["n"] else "-",
            len(l), cl["n"] / max(1, len(l)), ("%+.2f" % swing(cl)) if cl["n"] else "-"))

    if cls:
        P("\n-- 4. The trade-on-contact build against the live bot on these maps (means; own / opponent)")
        for k, ok in (("meow live", "opp of live"), ("meow tc30", "opp of tc30")):
            s2, o2 = sel[k], sel.get(ok, [])
            line = "   %-10s games %-3d won %-3d |" % (k, len(s2), sum(X.won(g, s) for g, s in s2))
            for Rr in (100, 150, 200, 300, 400):
                u = t = lg = n = ou = ot = ol = 0
                for g, side in s2:
                    d1 = g1[g["gid"]]["d"]
                    a, b = X.stats_at(d1, Rr, side), X.stats_at(d1, Rr, X.other(side))
                    if a is None or b is None:
                        continue
                    n += 1
                    u += a[0]; t += a[1]; lg += a[2]
                    ou += b[0]; ot += b[1]; ol += b[2]
                n = max(1, n)
                line += " r%d: units %.0f:%.0f total %.0f:%.0f longest %.0f:%.0f |" % (Rr, u / n, ou / n, t / n, ot / n, lg / n, ol / n)
            P(line)
            c = rams(s2, lambda r: True)
            co = rams(o2, lambda r: True)
            P("      rams started %.1f a game (swing %+.2f); the opponent starts %.1f a game (swing %+.2f)" % (
                c["n"] / max(1, len(s2)), swing(c) or 0, co["n"] / max(1, len(o2)), swing(co) or 0))
            ends = Counter()
            for g, side in s2:
                d1 = g1[g["gid"]]["d"]
                e = d1["end"]
                es = X.other(side)
                if e["rounds"] < 500:
                    ends["wiped out" if not X.won(g, side) else "wiped them"] += 1
                else:
                    ends["r500 own queen %s / hers %s" % ("alive" if e["qalive"][side] else "dead", "alive" if e["qalive"][es] else "dead")] += 1
            P("      how the games ended:", dict(ends))
out.close()
