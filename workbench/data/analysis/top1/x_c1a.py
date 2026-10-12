#!/usr/bin/env python3
"""Candidate 1, attack A: my recount of the in-view ram chances on the enemy queen, against B's table.
Reads x_out/c1/ (x_c1.py). Output: x_out/c1a.txt"""
import sys
from collections import Counter, defaultdict

import x_load as X

out = open("x_out/c1a.txt", "w")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


gs = [g for g in X.games("c1") if g["d"]]
P("games with data:", len(gs))

# ---- columns: (label, list of (game, side))
cols = defaultdict(list)
for g in gs:
    if not X.is_csv(g):
        continue
    for side in "AB":
        team = g[side]
        if not X.in_study(g, side):
            continue
        if team == X.ME:
            cols["meow all"].append((g, side))
            cols["meow live" if X.build(g) == "live" else "meow test builds"].append((g, side))
            cols["opp on our queen"].append((g, X.other(side)))
        if team in X.TOP3:
            cols[X.NAMES[team]].append((g, side))
order = ["meow all", "meow live", "meow test builds", "opp on our queen", "Vibing++", "SSS", "forgot"]
P("column sizes:", {k: len(cols[k]) for k in order})


def bucket(L):
    return "2-3" if L <= 3 else "4" if L == 4 else "5-9" if L <= 9 else "10-12" if L <= 12 else "13+"


BUCKETS = ["2-3", "4", "5-9", "10-12", "13+"]


def chances(g, side, key):
    """In-view chances of `side` under path test `key` (dS strict, dV strict-in-view, dW walls only)."""
    for c in g["d"]["chances"]:
        if c["side"] != side or c.get("far"):
            continue
        if c["cheb"] > 3:
            continue
        if c.get(key) is None:
            continue
        yield c


for key, name in (("dS", "STRICT (every body blocks; the bot's own test)"), ("dV", "STRICT, path inside own 7x7 view"),
                  ("dW", "WALLS ONLY (bodies ignored)")):
    P("\n== In-view chances taken, path test:", name)
    P("%-22s" % "attacker" + "".join("%-22s" % k for k in order))
    tab = {k: Counter() for k in order}
    for k in order:
        for g, side in cols[k]:
            for c in chances(g, side, key):
                b = bucket(c["L"])
                tab[k][b, "n"] += 1
                tab[k][b, "t"] += c["taken"]
    for b in BUCKETS:
        P("%-22s" % b + "".join("%-22s" % X.frac(tab[k][b, "t"], tab[k][b, "n"]) for k in order))
    for lab, bs in (("all <=12", BUCKETS[:4]), ("all", BUCKETS)):
        P("%-22s" % lab + "".join("%-22s" % X.frac(sum(tab[k][b, "t"] for b in bs), sum(tab[k][b, "n"] for b in bs)) for k in order))

# ---- detail rows on the strict test
P("\n== Strict test, detail (attackers of 12 or shorter unless said)")
rows = [
    ("attacker is team's longest (no longer own dragon)", lambda c: c["longer"] == 0),
    ("own queen alive", lambda c: c["oq"] > 0),
    ("own queen dead", lambda c: c["oq"] == 0),
    ("rounds 0-99", lambda c: c["r"] < 100),
    ("rounds 100-299", lambda c: 100 <= c["r"] < 300),
    ("rounds 300+", lambda c: c["r"] >= 300),
    ("free (dS <= ceil(L/4))", lambda c: c["dS"] <= -(-c["L"] // 4)),
    ("1 paid step", lambda c: c["dS"] - (-(-c["L"] // 4)) == 1),
    ("2 paid steps", lambda c: c["dS"] - (-(-c["L"] // 4)) == 2),
    ("3+ paid steps", lambda c: c["dS"] - (-(-c["L"] // 4)) >= 3),
    ("not outnumbered (own_h >= en_h)", lambda c: c["own_h"] >= c["en_h"]),
    ("outnumbered (own_h < en_h)", lambda c: c["own_h"] < c["en_h"]),
    ("alone with her (own_h 0, en_h 1)", lambda c: c["own_h"] == 0 and c["en_h"] == 1),
    ("queen 2-3 long", lambda c: c["qL"] <= 3),
    ("queen 4-7 long", lambda c: 4 <= c["qL"] <= 7),
    ("queen 8+ long", lambda c: c["qL"] >= 8),
    ("path leaves own view (dV None)", lambda c: c["dV"] is None),
]
P("%-48s" % "" + "".join("%-20s" % k for k in order))
for lab, f in rows:
    line = "%-48s" % lab
    for k in order:
        n = t = 0
        for g, side in cols[k]:
            for c in chances(g, side, "dS"):
                if c["L"] <= 12 and f(c):
                    n += 1
                    t += c["taken"]
        line += "%-20s" % X.frac(t, n)
    P(line)

# ---- game level
P("\n== Games (strict test)")
P("%-48s" % "" + "".join("%-20s" % k for k in order))
res = {k: Counter() for k in order}
for k in order:
    for g, side in cols[k]:
        d = g["d"]
        es = X.other(side)
        qd = d["qdeath"].get(es)
        rammed = bool(qd and qd["reason"] == "headon" and qd.get("actor_team") == side)
        ch = list(chances(g, side, "dS"))
        ch12 = [c for c in ch if c["L"] <= 12]
        res[k]["n"] += 1
        res[k]["rammed"] += rammed
        res[k]["chance"] += bool(ch)
        res[k]["chance12"] += bool(ch12)
        res[k]["chance_norams"] += bool(ch) and not rammed
        res[k]["chance12_norams"] += bool(ch12) and not rammed
        res[k]["q_alive_end"] += d["end"]["qalive"][es]
        res[k]["first_taken"] += bool(ch12) and ch12[0]["taken"]
        res[k]["ram_far"] += rammed and not any(c["taken"] for c in ch)
for lab, f in (("this side rammed the enemy queen", "rammed"), ("had an in-view chance (any length)", "chance"),
               ("had an in-view chance (<=12)", "chance12"), ("had a chance (<=12) and never rammed her", "chance12_norams"),
               ("had a chance (any) and never rammed her", "chance_norams"), ("first chance (<=12) taken", "first_taken"),
               ("rammed her without an in-view strict chance turn", "ram_far"),
               ("enemy queen alive at the end", "q_alive_end")):
    P("%-48s" % lab + "".join("%-20s" % X.frac(res[k][f], res[k]["n"]) for k in order))

# ---- queen ids
bad = [g["gid"] for g in gs if sorted(g["d"]["q"].values()) != [0, 1]]
P("\nqueen ids other than {0,1}:", len(bad), bad[:10])
P("queen id by side A:", Counter(g["d"]["q"]["A"] for g in gs))
