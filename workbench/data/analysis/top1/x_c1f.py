#!/usr/bin/env python3
"""Candidate 1, attack F: the online trials recounted from their replays (own code on x_out/c1/).
Every run of ours (games.csv battle_id, plus the smoke runs that are not in games.csv: qh31b, qn23), one line each:
wins, in-view chances taken by attacker length, games in which we rammed her queen, her queen dead at the end, the
four end states, our queen. Then the paired comparison old/new by (opponent, map) for qh31 and qh31b.
Schooltime is left out unless said. Output: x_out/c1f.txt"""
from collections import Counter, defaultdict

import x_load as X

out = open("x_out/c1f.txt", "w")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


gs = [g for g in X.games("c1") if g["d"]]
mine = [(g, X.side_of(g, X.ME)) for g in gs if X.side_of(g, X.ME)]


def inview(g, side, maxL=99):
    return [c for c in g["d"]["chances"] if c["side"] == side and not c.get("far") and c["cheb"] <= 3
            and c.get("dS") is not None and c["L"] <= maxL]


def stats(sel):
    c = Counter()
    hr, orr = [], []
    for g, side in sel:
        d = g["d"]
        es = X.other(side)
        c["games"] += 1
        c["won"] += X.won(g, side)
        ch = inview(g, side)
        for x in ch:
            k = "s" if x["L"] <= 3 else "m" if x["L"] == 4 else "l"
            c["n_" + k] += 1
            c["t_" + k] += x["taken"]
        qd = d["qdeath"].get(es)
        rammed = bool(qd and qd["reason"] == "headon" and qd.get("actor_team") == side)
        c["rammed"] += rammed
        if rammed:
            c["rammed_small"] += qd.get("actor_L", 9) <= 4
        c["her_dead"] += not d["end"]["qalive"][es]
        if qd:
            hr.append(qd["r"])
        oqd = d["qdeath"].get(side)
        c["our_alive"] += d["end"]["qalive"][side]
        if oqd:
            orr.append(oqd["r"])
            c["our_rammed"] += oqd["reason"] == "headon" and oqd.get("actor_team") == es
        c["chance_no_ram"] += bool(ch) and not rammed
        e = d["end"]
        c["end_%s%s" % ("A" if e["qalive"][side] else "D", "A" if e["qalive"][es] else "D")] += 1
        c["wipe_loss"] += e["rounds"] < 500 and not X.won(g, side)
        c["wipe_win"] += e["rounds"] < 500 and X.won(g, side)
    c["her_death_median"] = sorted(hr)[len(hr) // 2] if hr else -1
    c["our_death_median"] = sorted(orr)[len(orr) // 2] if orr else -1
    return c


def line(name, c):
    return ("%-22s games %-3d won %-13s | chances taken: 2-3-long %-13s 4-long %-9s 5+ %-10s | we rammed her %-12s (by <=4: %d) | "
            "chance, no ram %-3d | her queen dead at end %-12s (median r%d) | ours alive %-3d (death median r%d, rammed %d) | "
            "end own/her A/D %d, A/A %d, D/D %d, D/A %d | wiped out %d, wiped them %d") % (
        name, c["games"], X.frac(c["won"], c["games"]), X.frac(c["t_s"], c["n_s"]), X.frac(c["t_m"], c["n_m"]),
        X.frac(c["t_l"], c["n_l"]), X.frac(c["rammed"], c["games"]), c["rammed_small"], c["chance_no_ram"],
        X.frac(c["her_dead"], c["games"]), c["her_death_median"], c["our_alive"], c["our_death_median"], c["our_rammed"],
        c["end_AD"], c["end_AA"], c["end_DD"], c["end_DA"], c["wipe_loss"], c["wipe_win"])


sets = sorted({g["set"] for g, s in mine})
P("== Every run of ours, opponents rated 2000+, Schooltime left out")
for s in sets:
    sel = [(g, sd) for g, sd in mine if g["set"] == s and X.in_study(g, sd)]
    if sel:
        P(line(s, stats(sel)))
P("\n== The same with Schooltime (the team's own win counts include it)")
for s in sets:
    sel = [(g, sd) for g, sd in mine if g["set"] == s and X.opp(g, sd)[2] >= 2000]
    if sel:
        c = stats(sel)
        P("%-22s games %-3d won %s" % (s, c["games"], X.frac(c["won"], c["games"])))

P("\n== Pooled: live bot against every hunt build")
live = [(g, sd) for g, sd in mine if X.build(g) == "live" and X.in_study(g, sd) and X.opp(g, sd)[0] in (X.T4, X.WHQ)]
P(line("live, test4+WHQ", stats(live)))
for names in (("qh31-test-new",), ("qh31b-test-new",), ("qh31-test-new", "qh31b-test-new")):
    sel = [(g, sd) for g, sd in mine if g["set"] in names and X.in_study(g, sd)]
    P(line("+".join(n.replace("-test-new", "") for n in names), stats(sel)))
for names in (("qh31-test-old",), ("qh31b-test-old",), ("qh31-test-old", "qh31b-test-old")):
    sel = [(g, sd) for g, sd in mine if g["set"] in names and X.in_study(g, sd)]
    P(line("+".join(n.replace("-test-old", "") for n in names) + " old", stats(sel)))
sel = [(g, sd) for g, sd in mine if g["set"] == "qh31b-dev1-new" and X.in_study(g, sd)]
P(line("qh31b dev1 new", stats(sel)))
sel = [(g, sd) for g, sd in mine if g["set"] == "qh31b-dev1-old" and X.in_study(g, sd)]
P(line("qh31b dev1 old", stats(sel)))


def pairs(old, new):
    P("\n== Pairs %s / %s by (opponent, map): result old -> new, did we ram her queen old -> new, her queen dead at end old -> new" % (old, new))
    a = {(X.opp(g, sd)[0], g["map"]): (g, sd) for g, sd in mine if g["set"] == old}
    b = {(X.opp(g, sd)[0], g["map"]): (g, sd) for g, sd in mine if g["set"] == new}
    cnt = Counter()
    for key in sorted(set(a) & set(b), key=str):
        (g0, s0), (g1, s1) = a[key], b[key]
        if g0["map"] == "Schooltime":
            continue

        def info(g, sd):
            d = g["d"]
            es = X.other(sd)
            qd = d["qdeath"].get(es)
            rammed = bool(qd and qd["reason"] == "headon" and qd.get("actor_team") == sd)
            return X.won(g, sd), rammed, not d["end"]["qalive"][es], (qd["r"] if qd else None), d["end"]["qalive"][sd]

        i0, i1 = info(g0, s0), info(g1, s1)
        cnt["pairs"] += 1
        cnt["win %d->%d" % (i0[0], i1[0])] += 1
        cnt["ram %d->%d" % (i0[1], i1[1])] += 1
        kind = ("ram gained" if (i1[1] and not i0[1]) else "ram lost" if (i0[1] and not i1[1]) else "ram same")
        cnt[kind + ": new won"] += i1[0]
        cnt[kind + ": old won"] += i0[0]
        cnt[kind + ": n"] += 1
        P("   %-14s %-16s  won %d -> %d | rammed her %d -> %d | her queen dead at end %d -> %d (death round %s -> %s) | our queen alive %d -> %d" % (
            X.NAMES.get(key[0], key[0]), key[1], i0[0], i1[0], i0[1], i1[1], i0[2], i1[2], i0[3], i1[3], i0[4], i1[4]))
    P("   summary:", dict(sorted(cnt.items())))


pairs("qh31-test-old", "qh31-test-new")
pairs("qh31b-test-old", "qh31b-test-new")
pairs("qh31b-dev1-old", "qh31b-dev1-new")
out.close()
