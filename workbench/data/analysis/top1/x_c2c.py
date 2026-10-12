#!/usr/bin/env python3
"""Candidate 2, attacks E and I: (1) cut against shed: what becomes of a boxed-in queen of 6 or more by what she
did, per team; (2) do own heads near the queen change what happens when an enemy head is in view; (3) the mirror:
turns that end in a visible reach, both sides of our games. Own code on x_out/c2/. Output: x_out/c2c.txt"""
from collections import Counter, defaultdict

import x_load as X

out = open("x_out/c2c.txt", "w")


def use(g, side, pred):
    """The study's filter, also for the other side of our own games."""
    if not pred(g, side):
        return False
    o = X.other(side)
    return X.in_study(g, side) or (g[o] == X.ME and X.in_study(g, o))


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


gs = [g for g in X.games("c2") if g["d"] and X.is_csv(g)]
GROUPS = [("meow", lambda g, s: g[s] == X.ME), ("our opponents", lambda g, s: g[X.other(s)] == X.ME),
          ("Vibing++", lambda g, s: g[s] == X.VIB), ("SSS", lambda g, s: g[s] == X.SSS), ("forgot", lambda g, s: g[s] == X.FORGOT)]

P("== 1. A boxed-in queen of 6 or more: first such split of an episode (no boxed split in the 3 rounds before), by what she did")
for name, pred in GROUPS:
    c = defaultdict(Counter)
    for g in gs:
        for side in "AB":
            if not use(g, side, pred):
                continue
            d = g["d"]
            qd = d["qdeath"].get(side)
            sp = [s for s in d["splits"] if s["side"] == side and s["n_legal"] == 0 and s["L"] >= 6]
            last = -99
            for s in sp:
                first = s["r"] - last > 3
                last = s["r"]
                if not first:
                    continue
                kind = "cut (keeps 2-3)" if (s["keep"] <= 3 and s["child"] > 2) else "shed 2" if s["child"] == 2 else "other"
                k = c[kind]
                k["n"] += 1
                k["L"] += s["L"]
                dr = qd["r"] if qd else None
                k["dead within 5 rounds"] += dr is not None and dr - s["r"] <= 5
                k["dead within 20 rounds"] += dr is not None and dr - s["r"] <= 20
                k["alive at the end"] += dr is None
                k["game won"] += X.won(g, side)
                k["big queen (15+)"] += s["L"] >= 15
                if s["L"] >= 15:
                    k["big: dead within 20"] += dr is not None and dr - s["r"] <= 20
                    k["big: game won"] += X.won(g, side)
    for kind in ("cut (keeps 2-3)", "shed 2", "other"):
        k = c[kind]
        if k["n"]:
            P("   %-14s %-16s n=%-4d mean length %4.1f | dead within 5 rounds %-4s within 20 %-4s alive at the end %-4s game won %-4s | 15 or longer: n=%d, dead within 20 %s, game won %s" % (
                name, kind, k["n"], k["L"] / k["n"], X.pct(k["dead within 5 rounds"], k["n"]), X.pct(k["dead within 20 rounds"], k["n"]),
                X.pct(k["alive at the end"], k["n"]), X.pct(k["game won"], k["n"]), k["big queen (15+)"],
                X.pct(k["big: dead within 20"], k["big queen (15+)"]), X.pct(k["big: game won"], k["big queen (15+)"])))

P("\n== 2. Turns with an enemy head in her view: rammed that round, by the number of other own heads within 6 steps of her")
for name, pred in GROUPS:
    c = defaultdict(Counter)
    for g in gs:
        for side in "AB":
            if not use(g, side, pred):
                continue
            for t in g["d"]["turns"]:
                if t["side"] != side or t["seen"] == 0 or t["L"] > 3:
                    continue
                k = min(3, t["own6"])
                rammed = bool(t["death"] and not t["death"].get("own_move") and t["death"]["reason"] == "headon" and t["death"].get("actor_team") != side)
                c[k]["n"] += 1
                c[k]["rammed"] += rammed
                near = any(e[4] and e[6] is not None and e[6] <= 3 for e in t["ens"])
                if near:
                    c[k]["near_n"] += 1
                    c[k]["near_rammed"] += rammed
    P("   %-14s (queen 2-3 long) own heads within 6 steps 0 / 1 / 2 / 3+: rammed that round %s | with an enemy head within 3 steps: %s" % (
        name, " / ".join("%.1f%% of %d" % (100.0 * c[k]["rammed"] / max(1, c[k]["n"]), c[k]["n"]) for k in range(4)),
        " / ".join("%.0f%% of %d" % (100.0 * c[k]["near_rammed"] / max(1, c[k]["near_n"]), c[k]["near_n"]) for k in range(4))))

P("\n== 3. The mirror in our 401 games (pearl-paid reach, real board after her move): turns that end inside a visible reach, per 1,000 queen-rounds, and how often they are punished")
for name, pred in (("our queen", lambda g, s: g[s] == X.ME), ("their queen (our opponents)", lambda g, s: g[X.other(s)] == X.ME),
                   ("our queen vs test4", lambda g, s: g[s] == X.ME and X.opp(g, s)[0] == X.T4), ("test4's queen vs us", lambda g, s: g[s] == X.T4 and g[X.other(s)] == X.ME),
                   ("our queen vs WeHaveQuizzes", lambda g, s: g[s] == X.ME and X.opp(g, s)[0] == X.WHQ), ("WeHaveQuizzes's queen vs us", lambda g, s: g[s] == X.WHQ and g[X.other(s)] == X.ME),
                   ("top three's queens", lambda g, s: g[s] in X.TOP3)):
    c = Counter()
    for g in gs:
        for side in "AB":
            if not use(g, side, pred):
                continue
            d = g["d"]
            c["qr"] += d["qrounds"][side]
            for t in d["turns"]:
                if t["side"] != side or t["seen"] == 0:
                    continue
                own = bool(t["death"] and t["death"].get("own_move"))
                if own:
                    continue
                if t.get("endp_seen") is not None:
                    c["in"] += 1
                    c["in_rammed"] += bool(t["death"] and t["death"]["reason"] == "headon" and t["death"].get("actor_team") != side)
                if t.get("end_seen") is not None:
                    c["in_plain"] += 1
                    c["in_plain_rammed"] += bool(t["death"] and t["death"]["reason"] == "headon" and t["death"].get("actor_team") != side)
    P("   %-30s ends in reach %.2f per 1,000 queen-rounds (%d turns), rammed on %s | plain reach (no pearl-paid steps): %.2f per 1,000, rammed on %s" % (
        name, 1000.0 * c["in"] / max(1, c["qr"]), c["in"], X.pct(c["in_rammed"], c["in"]),
        1000.0 * c["in_plain"] / max(1, c["qr"]), X.pct(c["in_plain_rammed"], c["in_plain"])))
out.close()
