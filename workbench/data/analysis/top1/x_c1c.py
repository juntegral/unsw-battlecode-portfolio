#!/usr/bin/env python3
"""Candidate 1, attack C (what happens next). Own code on x_out/c1/.

1. State table: P(win | round R, economy band at R, own queen alive, enemy queen alive) for meow, the top three, all teams.
2. After a real ram on the enemy queen at round r in state (band, own queen): how did those games end, against games
   in the same state at the same checkpoint in which she was alive?
3. What B's rule would add, priced with the state table instead of the "strict" reading: every game with a first untaken
   in-view chance, at the state of that turn.
4. What the team that lost its queen builds (its longest non-queen dragon at the end) and how the side that spent a long
   dragon or its longest dragon on the ram ended.
Output: x_out/c1c.txt"""
from collections import Counter, defaultdict

import x_load as X

out = open("x_out/c1c.txt", "w")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


gs = [g for g in X.games("c1") if g["d"] and X.is_csv(g)]
CHECK = (50, 100, 150, 200, 250, 300, 350, 400, 450)


def q_alive_at(d, side, R):
    qd = d["qdeath"].get(side)
    return qd is None or qd["r"] >= R


def state_at(g, side, R):
    """(band, own queen alive, enemy queen alive) at the start of round R, or None if the game was over."""
    d = g["d"]
    if d["end"]["rounds"] <= R:
        return None
    own = X.stats_at(d, R, side)
    en = X.stats_at(d, R, X.other(side))
    if own is None or en is None or en[1] == 0 or own[1] == 0:
        return None
    return (X.band(own[1] / en[1]), q_alive_at(d, side, R), q_alive_at(d, X.other(side), R))


def table(pred):
    T = defaultdict(lambda: [0, 0])  # (R, band, oq, eq) -> [wins, n]
    for g in gs:
        for side in "AB":
            if not X.in_study(g, side) or not pred(g, side):
                continue
            for R in CHECK:
                st = state_at(g, side, R)
                if st is None:
                    continue
                c = T[(R,) + st]
                c[0] += X.won(g, side)
                c[1] += 1
    return T


GROUPS = [("meow", lambda g, s: g[s] == X.ME), ("top three", lambda g, s: g[s] in X.TOP3),
          ("every team rated 2000+ in the data", lambda g, s: g[s + "e"] >= 2000 or g[s] == X.ME)]
TAB = {}
for name, pred in GROUPS:
    T = table(pred)
    TAB[name] = T
    P("\n== 1. %s: win rate by state at round R. Cells: own queen / her queen = alive-alive, alive-DEAD, dead-alive, dead-DEAD" % name)
    P("%-5s %-8s %-18s %-18s %-18s %-18s   gain from her death: own alive | own dead" % ("R", "band", "A/A", "A/D", "D/A", "D/D"))
    for R in (100, 200, 300, 400):
        for b in range(4):
            cells = [T[(R, b, oq, eq)] for oq, eq in ((True, True), (True, False), (False, True), (False, False))]
            def r(c):
                return (c[0] / c[1]) if c[1] else None
            g1 = (r(cells[1]) - r(cells[0])) if cells[0][1] and cells[1][1] else None
            g2 = (r(cells[3]) - r(cells[2])) if cells[2][1] and cells[3][1] else None
            P("%-5d %-8s " % (R, X.BAND_NAMES[b]) + " ".join("%-18s" % X.frac(c[0], c[1]) for c in cells) +
              "   %s | %s" % ("%+.0f" % (100 * g1) if g1 is not None else "  -", "%+.0f" % (100 * g2) if g2 is not None else "  -"))


def nearest_check(r):
    return min(CHECK, key=lambda R: (abs(R - r), R))


def rate(T, R, b, oq, eq, fallback=True):
    c = T.get((R, b, oq, eq))
    if c and c[1] >= 5:
        return c[0] / c[1]
    if not fallback:
        return None
    # pool over neighbouring checkpoints, then over the queen state of the own side
    w = n = 0
    for R2 in CHECK:
        if abs(R2 - R) <= 100:
            c = T.get((R2, b, oq, eq))
            if c:
                w += c[0]
                n += c[1]
    if n >= 5:
        return w / n
    w = n = 0
    for R2 in CHECK:
        c = T.get((R2, b, oq, eq))
        if c:
            w += c[0]
            n += c[1]
    return w / n if n else None


def chance_state(c):
    return X.band(c["own"][1] / max(1, c["en"][1])), c["oq"] > 0


P("\n== 2. Real rams on the enemy queen: how those games ended, against the state table (same checkpoint, band, own queen; her queen alive)")
for name, pred in GROUPS:
    T = TAB[name]
    rows = []
    for g in gs:
        for side in "AB":
            if not X.in_study(g, side) or not pred(g, side):
                continue
            for c in g["d"]["chances"]:
                if c["side"] == side and c.get("taken") and not c.get("far"):
                    b, oq = chance_state(c)
                    R = nearest_check(c["r"])
                    rows.append((c, b, oq, R, X.won(g, side), g))
    P("\n-- %s: %d rams" % (name, len(rows)))
    for lab, f in (("all", lambda c: True), ("attacker 2-4", lambda c: c["L"] <= 4), ("attacker 5-12", lambda c: 5 <= c["L"] <= 12),
                   ("attacker 13+", lambda c: c["L"] >= 13), ("attacker is the team's longest, 5+", lambda c: c["longer"] == 0 and c["L"] >= 5),
                   ("attacker is the team's longest, 10+", lambda c: c["longer"] == 0 and c["L"] >= 10),
                   ("rounds 0-99", lambda c: c["r"] < 100), ("rounds 100-299", lambda c: 100 <= c["r"] < 300), ("rounds 300+", lambda c: c["r"] >= 300)):
        sel = [x for x in rows if f(x[0])]
        if not sel:
            continue
        w = sum(x[4] for x in sel)
        ea = [rate(T, x[3], x[1], x[2], True) for x in sel]
        ed = [rate(T, x[3], x[1], x[2], False) for x in sel]
        ea = [v for v in ea if v is not None]
        ed = [v for v in ed if v is not None]
        P("   %-36s n=%-4d won %-16s | same state, her queen alive: %4.0f%% | same state, her queen dead (table): %4.0f%%" % (
            lab, len(sel), X.frac(w, len(sel)), 100 * sum(ea) / max(1, len(ea)), 100 * sum(ed) / max(1, len(ed))))
    # by own queen state
    for oq in (True, False):
        sel = [x for x in rows if x[2] == oq]
        if sel:
            w = sum(x[4] for x in sel)
            ea = [v for v in (rate(T, x[3], x[1], x[2], True) for x in sel) if v is not None]
            P("   own queen %-5s at the ram: n=%-4d won %-16s | same state, her queen alive: %4.0f%%" % (
                "alive" if oq else "dead", len(sel), X.frac(w, len(sel)), 100 * sum(ea) / max(1, len(ea))))

P("\n== 3. What the rule would add in OUR games, priced by state tables (first untaken in-view chance of each game; attackers <= 12)")
for tname in ("meow", "top three", "every team rated 2000+ in the data"):
    T = TAB[tname]
    for label, pred in (("meow all 401", lambda g: True), ("meow live", lambda g: X.build(g) == "live")):
        tot_now = tot_dead = tot_alive = 0.0
        n = wins = 0
        for g in gs:
            side = X.side_of(g, X.ME)
            if side is None or not X.in_study(g, side) or not pred(g):
                continue
            ch = [c for c in g["d"]["chances"] if c["side"] == side and not c.get("far") and c["cheb"] <= 3
                  and c.get("dS") is not None and c["L"] <= 12]
            if not ch or ch[0]["taken"]:
                continue
            c = ch[0]
            b, oq = chance_state(c)
            R = nearest_check(c["r"])
            pd = rate(T, R, b, oq, False)
            pa = rate(T, R, b, oq, True)
            if pd is None or pa is None:
                continue
            n += 1
            wins += X.won(g, side)
            tot_dead += pd
            tot_alive += pa
        P("   table of %-36s %-13s: %d games with an untaken first chance, really won %d; table says %.1f wins with her alive at that state, %.1f with her dead: gain %+.1f wins (against the real %d: %+.1f)"
          % (tname, label, n, wins, tot_alive, tot_dead, tot_dead - tot_alive, wins, tot_dead - wins))

P("\n== 4a. What a team builds once its queen is dead: its longest NON-queen dragon at the end of round-500 games")
for name, pred in (("our opponents (in our 401 games)", lambda g, s: g[X.other(s)] == X.ME),
                   ("test4", lambda g, s: g[s] == X.T4), ("WeHaveQuizzes", lambda g, s: g[s] == X.WHQ),
                   ("top three", lambda g, s: g[s] in X.TOP3), ("meow", lambda g, s: g[s] == X.ME)):
    P("-- " + name)
    for lo, hi in ((0, 80), (80, 160), (160, 9999)):
        res = defaultdict(list)
        for g in gs:
            for side in "AB":
                if not pred(g, side) or g["map"] == "Schooltime":
                    continue
                d = g["d"]
                if d["end"]["rounds"] < 500:
                    continue
                st = X.stats_at(d, 400, side)
                if st is None or not (lo <= st[1] < hi):
                    continue
                qd = d["qdeath"].get(side)
                key = "queen alive at end" if qd is None else "queen dead before 300" if qd["r"] < 300 else "queen died 300+"
                qid = d["q"][side]
                nonq = [L for L, did in d["end"]["tops"][side] if did != qid]
                best = nonq[0] if nonq else 0
                res[key].append((best, d["end"]["st"][side][2], st[1]))
        line = "   total length at round 400 in [%d,%d): " % (lo, hi)
        for key in ("queen dead before 300", "queen died 300+", "queen alive at end"):
            v = sorted(res[key])
            if v:
                line += "%s n=%d median longest non-queen %d (longest incl. queen %d) | " % (
                    key, len(v), v[len(v) // 2][0], sorted(x[1] for x in v)[len(v) // 2])
        P(line)

P("\n== 4b. Rams by the team's longest dragon (10+): each game")
for name, team in (("Vibing++", X.VIB), ("SSS", X.SSS), ("meow", X.ME), ("forgot", X.FORGOT)):
    rows = []
    for g in gs:
        side = X.side_of(g, team)
        if side is None or not X.in_study(g, side):
            continue
        for c in g["d"]["chances"]:
            if c["side"] == side and c.get("taken") and not c.get("far") and c["longer"] == 0 and c["L"] >= 10:
                d = g["d"]
                es = X.other(side)
                rows.append((g["gid"], g["map"], c["r"], c["L"], c["qL"], c["oq"], c["own"][1], c["en"][1],
                             "WON" if X.won(g, side) else "lost", d["end"]["rounds"],
                             d["end"]["st"][side][2], d["end"]["st"][es][2]))
    P("-- %s: %d such rams; won %d" % (name, len(rows), sum(1 for r in rows if r[8] == "WON")))
    for r in rows[:40]:
        P("   game %d %-16s r%-3d attacker %-3d her queen %-3d own queen %-3d totals %d vs %d -> %s (rounds %d, final longest %d vs %d)" % r)
out.close()
