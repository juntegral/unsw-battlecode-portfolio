#!/usr/bin/env python3
"""Candidate 2, attacks B, C, D, G: what follows a safe step, what a saved queen is worth, and what the rule costs.
Reads x_out/c2/ (version 2, pearl-paid reach) and x_out/c1/ (end states). Output: x_out/c2b.txt"""
from collections import Counter, defaultdict

import x_load as X

out = open("x_out/c2b.txt", "w")


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


g2 = [g for g in X.games("c2") if g["d"] and X.is_csv(g)]
g1 = {g["gid"]: g for g in X.games("c1") if g["d"]}
I = 6  # pearl model index in an option


def cls(t):
    free = [o for o in t["opts"] if o[0] == "free"]
    safe = [o for o in free if o[I] == 0]
    roomy = [o for o in safe if o[4] >= 8 and not o[5]]
    start_in = t["startp_seen"] is not None
    own = bool(t["death"] and t["death"].get("own_move"))
    ends_in = (t.get("endp_seen") is not None) if not own else None
    return start_in, safe, roomy, ends_in, own


def groups():
    yield "meow all", lambda g, s: g[s] == X.ME
    yield "meow live", lambda g, s: g[s] == X.ME and X.build(g) == "live"
    yield "meow vs test4", lambda g, s: g[s] == X.ME and X.opp(g, s)[0] == X.T4
    yield "meow vs WeHaveQuizzes", lambda g, s: g[s] == X.ME and X.opp(g, s)[0] == X.WHQ
    yield "meow, maps over 600 cells", lambda g, s: g[s] == X.ME and g["cells"] > 600
    yield "meow, maps of 600 cells or fewer", lambda g, s: g[s] == X.ME and g["cells"] <= 600
    yield "top three", lambda g, s: g[s] in X.TOP3
    yield "top three vs test4/WHQ", lambda g, s: g[s] in X.TOP3 and X.opp(g, s)[0] in (X.T4, X.WHQ)
    yield "our opponents", lambda g, s: g[X.other(s)] == X.ME


def sel(pred):
    return [(g, s) for g in g2 for s in "AB" if use(g, s, pred)]


# ------------------------------------------------------------------ 1. after a safe step
P("== 1. The same situation, by what she did (pearl-paid reach model). Fate after the turn.")
for name, pred in groups():
    rows = Counter()
    for g, side in sel(pred):
        d = g["d"]
        qd = d["qdeath"].get(side)
        dr = qd["r"] if qd else None
        rammed_death = bool(qd and qd["reason"] == "headon" and not qd.get("own_move") and qd.get("actor_team") != side)
        endr = d["final"]["rounds"]
        for t in d["turns"]:
            if t["side"] != side or t["seen"] == 0:
                continue
            start_in, safe, roomy, ends_in, own = cls(t)
            if own or not safe:
                continue
            small_near = any(e[4] and e[1] <= 4 and e[6] is not None and e[6] <= 4 for e in t["ens"])
            if start_in:
                sit = "S1 inside reach, safe step exists"
            elif small_near:
                sit = "S2 outside reach, small enemy within 4 steps, safe step exists"
            else:
                continue
            k = (sit, "ended in reach" if ends_in else "ended outside")
            rows[k, "n"] += 1
            if dr is not None and rammed_death:
                rows[k, "r0"] += dr == t["r"]
                rows[k, "r3"] += dr - t["r"] <= 3
                rows[k, "r10"] += dr - t["r"] <= 10
            if dr is not None:
                rows[k, "d10"] += dr - t["r"] <= 10
                rows[k, "d50"] += dr - t["r"] <= 50
            rows[k, "alive_end"] += dr is None
    P("-- " + name)
    for sit in ("S1 inside reach, safe step exists", "S2 outside reach, small enemy within 4 steps, safe step exists"):
        for e in ("ended outside", "ended in reach"):
            k = (sit, e)
            n = rows[k, "n"]
            if n:
                P("   %-64s %-15s n=%-5d rammed that round %-5s within 3 %-5s within 10 %-5s | dead (any cause) within 10 %-5s within 50 %-5s | alive at the end %s" % (
                    sit, e, n, X.pct(rows[k, "r0"], n, 1), X.pct(rows[k, "r3"], n), X.pct(rows[k, "r10"], n),
                    X.pct(rows[k, "d10"], n), X.pct(rows[k, "d50"], n), X.pct(rows[k, "alive_end"], n)))

# ------------------------------------------------------------------ 2. survival of our queen from round r
P("\n== 2. Our queen alive at round r: how often is she alive at the end of the game? (and the top three's)")
for name, pred in (("meow all", lambda g, s: g[s] == X.ME), ("meow, maps over 600 cells", lambda g, s: g[s] == X.ME and g["cells"] > 600),
                   ("meow, maps of 600 or fewer", lambda g, s: g[s] == X.ME and g["cells"] <= 600), ("top three", lambda g, s: g[s] in X.TOP3),
                   ("top three vs test4/WHQ", lambda g, s: g[s] in X.TOP3 and X.opp(g, s)[0] in (X.T4, X.WHQ))):
    line = "   %-28s" % name
    S = {}
    for R in (0, 50, 100, 150, 200, 300, 400):
        a = e = 0
        for g, side in sel(pred):
            d = g["d"]
            qd = d["qdeath"].get(side)
            if d["final"]["rounds"] <= R:
                continue
            if qd is None or qd["r"] >= R:
                a += 1
                e += qd is None
        S[R] = e / max(1, a)
        line += " r%d: %d of %d = %s |" % (R, e, a, X.pct(e, a))
    P(line)

# ------------------------------------------------------------------ 3. the deaths the candidate touches and what they are worth
P("\n== 3. Our queen's deaths the candidate would touch, by what the game was (pearl model for the 'in reach' part)")


def survival_table(pred):
    """P(alive at the end | alive at round r), for r in steps of 25."""
    tab = {}
    for R in range(0, 500, 25):
        a = e = 0
        for g, side in sel(pred):
            d = g["d"]
            qd = d["qdeath"].get(side)
            if d["final"]["rounds"] <= R:
                continue
            if qd is None or qd["r"] >= R:
                a += 1
                e += qd is None
        tab[R] = (e / a) if a else 0.0
    return tab


S_me = survival_table(lambda g, s: g[s] == X.ME)
S_top = survival_table(lambda g, s: g[s] in X.TOP3)
S_top_t4 = survival_table(lambda g, s: g[s] in X.TOP3 and X.opp(g, s)[0] in (X.T4, X.WHQ))


def surv(tab, r):
    return tab[min(475, (r // 25) * 25 + 25)]


def death_kind(g, side):
    d = g["d"]
    qd = d["qdeath"].get(side)
    if qd is None:
        return "alive", None
    turn = None
    for t in d["turns"]:
        if t["side"] == side and t["r"] == qd["r"]:
            turn = t
    if qd.get("own_move"):
        if qd["reason"] == "headon":
            if turn is not None:
                free = [o for o in turn["opts"] if o[0] == "free"]
                safe = [o for o in free if o[I] == 0]
                return ("own ram, a free safe cell existed" if safe else "own ram, no safe cell"), turn
            return "own ram, no safe cell", turn
        if turn is not None and turn["n_legal"] == 0:
            # was it the turn after a cut?
            cut = any(s["side"] == side and s["n_legal"] == 0 and s["keep"] <= 3 and s["child"] > 2 and 0 < qd["r"] - s["r"] <= 5
                      for s in d["splits"])
            return ("boxed in, within 5 rounds of a cut" if cut else "boxed in"), turn
        return "other own move", turn
    if qd["reason"] != "headon" or qd.get("actor_team") == side:
        return "other", turn
    if turn is None or not qd.get("actor_seen"):
        cut = any(s["side"] == side and s["n_legal"] == 0 and s["keep"] <= 3 and s["child"] > 2 and 0 <= qd["r"] - s["r"] <= 5
                  for s in d["splits"])
        return ("rammed unseen, within 5 rounds of a cut" if cut else "rammed: killer not in her view"), turn
    start_in, safe, roomy, ends_in, own = cls(turn)
    if not safe:
        return "rammed: cornered", turn
    if ends_in is False:
        return "rammed on a cell the model called safe", turn
    return ("rammed: stayed in reach, safe step existed" if start_in else "rammed: stepped into reach, safe step existed"), turn


TOUCH = {"rammed: stayed in reach, safe step existed": "never end in a visible reach",
         "rammed: stepped into reach, safe step existed": "never end in a visible reach",
         "own ram, a free safe cell existed": "never ram",
         "boxed in, within 5 rounds of a cut": "shed 2, never cut",
         "rammed unseen, within 5 rounds of a cut": "shed 2, never cut"}
for label, pred in (("meow, all 401 games", lambda g: True), ("meow, live bot", lambda g: X.build(g) == "live"),
                    ("meow, maps over 600 cells", lambda g: g["cells"] > 600), ("meow, maps of 600 cells or fewer", lambda g: g["cells"] <= 600),
                    ("meow vs test4", lambda g: X.opp(g, X.side_of(g, X.ME))[0] == X.T4), ("meow vs WeHaveQuizzes", lambda g: X.opp(g, X.side_of(g, X.ME))[0] == X.WHQ)):
    res = defaultdict(Counter)
    kinds = Counter()
    for g in g2:
        side = X.side_of(g, X.ME)
        if side is None or not X.in_study(g, side) or not pred(g):
            continue
        kd, turn = death_kind(g, side)
        kinds[kd] += 1
        part = TOUCH.get(kd)
        if part is None:
            continue
        d1 = g1[g["gid"]]["d"]
        e = d1["end"]
        es = X.other(side)
        r = g["d"]["qdeath"][side]["r"]
        c = res[part]
        c["deaths"] += 1
        c["roomy"] += bool(turn and cls(turn)[2])
        if e["rounds"] < 500:
            c["wipe-out (no change)"] += 1
            continue
        if X.won(g, side):
            c["round-500 win already"] += 1
            continue
        her_alive = e["qalive"][es]
        if her_alive:
            c["round-500 loss, her queen alive"] += 1
            # a living queen of ours wins only if she is longer; ours would be 2-3 long: count nothing (strict: 0)
            continue
        c["round-500 loss, both dead (flips if ours lives)"] += 1
        c["strict"] += 1
        c["real_me"] += surv(S_me, r)
        c["real_top"] += surv(S_top, r)
        c["real_top_t4"] += surv(S_top_t4, r)
    P("-- %s: kinds of end: %s" % (label, dict(kinds.most_common())))
    tot = Counter()
    for part in ("never end in a visible reach", "shed 2, never cut", "never ram"):
        c = res[part]
        for k in c:
            tot[k] += c[k]
        P("   %-30s deaths %-4d (roomy safe step %-3d) | wipe-outs %-3d r500 wins %-3d r500 losses with her alive %-3d r500 losses both dead %-3d | flips: strict %d, if she then lives like our own queen %.1f, like a top-three queen %.1f, like a top-three queen against test4/WHQ %.1f" % (
            part, c["deaths"], c["roomy"], c["wipe-out (no change)"], c["round-500 win already"], c["round-500 loss, her queen alive"],
            c["round-500 loss, both dead (flips if ours lives)"], c["strict"], c["real_me"], c["real_top"], c["real_top_t4"]))
    P("   %-30s deaths %-4d | flips: strict %d, own survival %.1f, top-three survival %.1f, top three vs test4/WHQ %.1f" % (
        "ALL THREE PARTS", tot["deaths"], tot["strict"], tot["real_me"], tot["real_top"], tot["real_top_t4"]))

# ------------------------------------------------------------------ 4. cost: the turns the rule would change
P("\n== 4. The turns the rule would change (she ended in a visible reach although a safe step existed), our 401 games")
c = Counter()
for g in g2:
    side = X.side_of(g, X.ME)
    if side is None or not X.in_study(g, side):
        continue
    for t in g["d"]["turns"]:
        if t["side"] != side or t["seen"] == 0:
            continue
        start_in, safe, roomy, ends_in, own = cls(t)
        if own or not safe or not ends_in:
            continue
        c["turns"] += 1
        c["ate a pearl on it"] += t["ate"] > 0
        c["ate a pearl, rounds 0-99"] += t["ate"] > 0 and t["r"] < 100
        c["it was a split"] += t["kind"] == 1
        c["no roomy safe step (only a pocket or a portal step)"] += not roomy
        c["queen 2-3 long"] += t["L"] <= 3
        c["on a map of 600 cells or fewer"] += g["cells"] <= 600
        c["rounds 0-99"] += t["r"] < 100
        c["moved more than one step"] += t["n"] > 1
        # under the PLAIN model (the bot's existing pieces) would the turn be seen as in reach at all?
        plain_end = t.get("end_seen") is not None
        c["the plain (no-pearl) model also calls the end cell in reach"] += plain_end
P("   " + "; ".join("%s: %d" % kv for kv in c.most_common()))

# ------------------------------------------------------------------ 5. the queen as a fighter on small maps, and as attacker of the enemy queen
P("\n== 5. Our queen's own rams, and turns on which she could have rammed the ENEMY queen (plain reach), by map size")
for label, pred in (("maps of 600 cells or fewer", lambda g: g["cells"] <= 600), ("maps over 600 cells", lambda g: g["cells"] > 600)):
    c = Counter()
    for g in g2:
        side = X.side_of(g, X.ME)
        if side is None or not X.in_study(g, side) or not pred(g):
            continue
        d = g["d"]
        es = X.other(side)
        c["games"] += 1
        c["won"] += X.won(g, side)
        qd = d["qdeath"].get(side)
        ownram = bool(qd and qd.get("own_move") and qd["reason"] == "headon")
        if ownram:
            c["games in which she died ramming"] += 1
            c["... won"] += X.won(g, side)
            eqd = d["qdeath"].get(es)
            if eqd and eqd["r"] == qd["r"] and eqd["reason"] == "headon" and eqd.get("actor") == d["q"][side]:
                c["... her victim was the enemy queen"] += 1
                c["... ... won"] += X.won(g, side)
        turns_eq = [t for t in d["turns"] if t["side"] == side and t.get("eq_reach") is not None]
        if turns_eq:
            c["games with a turn on which she could ram the enemy queen"] += 1
            c["such turns"] += len(turns_eq)
    P("   %-28s %s" % (label, dict(c)))
out.close()
