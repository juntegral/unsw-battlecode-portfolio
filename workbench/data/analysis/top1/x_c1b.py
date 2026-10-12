#!/usr/bin/env python3
"""Candidate 1, attack B (cause or consequence). Own code on x_out/c1/.

1. Take-up of in-view chances per team against the team's rating, over ALL teams in the data.
2. Natural experiments: per (game, side) the FIRST in-view strict chance; compare games in which it was taken
   with games in which it was not, inside the same team, the same round band, the same economy band and the same
   state of the own queen. Outcomes: win, enemy queen dead at the end, end type.
3. A logistic fit of win on taken + economy + round + own queen (+ team), as a second way to hold those fixed.
Output: x_out/c1b.txt"""
import math
from collections import Counter, defaultdict

import x_load as X

out = open("x_out/c1b.txt", "w")


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.write(s + "\n")


gs = [g for g in X.games("c1") if g["d"] and X.is_csv(g)]


def inview(g, side, maxL=12):
    return [c for c in g["d"]["chances"] if c["side"] == side and not c.get("far") and c["cheb"] <= 3
            and c.get("dS") is not None and c["L"] <= maxL]


# ---------------------------------------------------------------- 1. per team
P("== 1. Take-up per team (in-view strict chances, attackers <= 12), every team with 15+ chances; opponents rated 2000+ or not")
team = defaultdict(lambda: Counter())
tname, telo = {}, defaultdict(list)
for g in gs:
    if g["map"] == "Schooltime":
        continue
    for side in "AB":
        t = g[side]
        tname[t] = g[side + "n"]
        telo[t].append(g[side + "e"])
        team[t]["games"] += 1
        team[t]["won"] += X.won(g, side)
        for c in inview(g, side):
            small = c["L"] <= 3
            team[t]["n"] += 1
            team[t]["t"] += c["taken"]
            team[t]["n_s" if small else "n_l"] += 1
            team[t]["t_s" if small else "t_l"] += c["taken"]
rows = []
for t, c in team.items():
    if c["n"] >= 15:
        rows.append((sum(telo[t]) / len(telo[t]), t, c))
rows.sort(reverse=True)
P("%-28s %5s %5s %6s  %-18s %-18s %-18s" % ("team", "elo", "games", "won", "all", "attacker 2-3", "attacker 4-12"))
xs, ys, ws = [], [], []
for elo, t, c in rows:
    P("%-28s %5.0f %5d %5.0f%%  %-18s %-18s %-18s" % (str(tname[t])[:27], elo, c["games"], 100 * c["won"] / c["games"],
                                                    X.frac(c["t"], c["n"]), X.frac(c["t_s"], c["n_s"]), X.frac(c["t_l"], c["n_l"])))
    xs.append(elo)
    ys.append(c["t"] / c["n"])
    ws.append(c["n"])


def corr(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else float("nan")


def rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i])
    r = [0] * len(v)
    for k, i in enumerate(o):
        r[i] = k
    return r


P("teams:", len(xs), " correlation of take-up share with elo: Pearson %.2f, Spearman %.2f" % (corr(xs, ys), corr(rank(xs), rank(ys))))
no_me = [(x, y) for (x, y), (elo, t, c) in zip(zip(xs, ys), rows) if t != X.ME]
P("without meow: Pearson %.2f, Spearman %.2f" % (corr([a for a, b in no_me], [b for a, b in no_me]),
                                                 corr(rank([a for a, b in no_me]), rank([b for a, b in no_me]))))
# win rate against take-up among the non-top teams
P("take-up under 60%:", [(str(tname[t])[:18], round(elo), X.pct(c["t"], c["n"])) for elo, t, c in rows if c["t"] / c["n"] < 0.6])

# ---------------------------------------------------------------- 2. natural experiments
P("\n== 2. First in-view chance of a game taken or not (per game and side; attackers <= 12; study filter: opponent 2000+, no Schooltime)")


def first_rows(pred, maxL=12):
    res = []
    for g in gs:
        for side in "AB":
            if not X.in_study(g, side) or not pred(g, side):
                continue
            ch = inview(g, side, maxL)
            if not ch:
                continue
            c = ch[0]
            d = g["d"]
            es = X.other(side)
            ratio = c["own"][1] / max(1, c["en"][1])
            res.append(dict(g=g, side=side, c=c, taken=c["taken"], win=X.won(g, side), rb=min(3, c["r"] // 100),
                            eb=X.band(ratio), ratio=ratio, oq=c["oq"] > 0, qdead_end=not d["end"]["qalive"][es],
                            oq_end=d["end"]["qalive"][side], rounds=d["end"]["rounds"], team=g[side], L=c["L"],
                            any_taken=any(x["taken"] for x in ch)))
    return res


def show(label, rows):
    t = [r for r in rows if r["taken"]]
    u = [r for r in rows if not r["taken"]]
    P("\n-- %s: %d games with a first chance; taken %d, not taken %d" % (label, len(rows), len(t), len(u)))
    if not t or not u:
        return

    def line(name, rs):
        n = len(rs)
        if not n:
            return "%-34s n=0" % name
        w = sum(r["win"] for r in rs)
        lo, hi = X.wilson(w, n)
        return "%-34s n=%-4d won %-16s [80%%: %2.0f-%2.0f%%]  her queen dead at end %-5s  wiped-out games %-5s median round %d  median ratio %.2f" % (
            name, n, X.frac(w, n), 100 * lo, 100 * hi, X.pct(sum(r["qdead_end"] for r in rs), n),
            X.pct(sum(r["rounds"] < 500 for r in rs), n), sorted(r["c"]["r"] for r in rs)[n // 2],
            sorted(r["ratio"] for r in rs)[n // 2])

    P(line("first chance taken", t))
    P(line("first chance NOT taken", u))
    P(line(" ... not taken, rammed her later", [r for r in u if r["any_taken"]]))
    P(line(" ... not taken, never rammed her", [r for r in u if not r["any_taken"]]))
    # stratified: economy band x own queen
    P("   by economy band at the chance (own/enemy total length) and own queen:    taken: won/n   |  not taken: won/n")
    num = den = 0.0
    num2 = den2 = 0.0
    for eb in range(4):
        for oq in (True, False):
            a = [r for r in t if r["eb"] == eb and r["oq"] == oq]
            b = [r for r in u if r["eb"] == eb and r["oq"] == oq]
            if not a and not b:
                continue
            wa, wb = sum(r["win"] for r in a), sum(r["win"] for r in b)
            P("   band %-7s own queen %-5s  %3d/%-3d %-5s | %3d/%-3d %-5s" % (
                X.BAND_NAMES[eb], "alive" if oq else "dead", wa, len(a), X.pct(wa, len(a)), wb, len(b), X.pct(wb, len(b))))
            if a and b:
                num += len(b) * (wa / len(a) - wb / len(b))
                den += len(b)
                num2 += len(a) * (wa / len(a) - wb / len(b))
                den2 += len(a)
    if den:
        P("   standardised difference in win rate, taken minus not taken, weighted like the NOT-taken games: %+.1f points over %d games"
          % (100 * num / den, den))
        P("   the same weighted like the taken games: %+.1f points" % (100 * num2 / den2))
    # by round band
    for rb in range(4):
        a = [r for r in t if r["rb"] == rb]
        b = [r for r in u if r["rb"] == rb]
        P("   rounds %d-%d: taken %s | not taken %s" % (rb * 100, rb * 100 + 99 if rb < 3 else 499,
                                                       X.frac(sum(r["win"] for r in a), len(a)), X.frac(sum(r["win"] for r in b), len(b))))


def logit(rows, with_team=False):
    """IRLS logistic regression of win on taken, log ratio, round/100, own queen alive (+ team dummies)."""
    try:
        import numpy as np
    except Exception:
        P("   (numpy missing, no fit)")
        return
    teams = sorted({r["team"] for r in rows}) if with_team else []
    Xm, y = [], []
    for r in rows:
        v = [1.0, 1.0 if r["taken"] else 0.0, math.log(max(0.05, r["ratio"])), r["c"]["r"] / 100.0, 1.0 if r["oq"] else 0.0]
        v += [1.0 if r["team"] == t else 0.0 for t in teams[1:]]
        Xm.append(v)
        y.append(1.0 if r["win"] else 0.0)
    A = np.array(Xm)
    yv = np.array(y)
    beta = np.zeros(A.shape[1])
    for _ in range(50):
        z = A @ beta
        p = 1 / (1 + np.exp(-z))
        W = p * (1 - p) + 1e-9
        H = A.T @ (A * W[:, None]) + 1e-6 * np.eye(A.shape[1])
        gvec = A.T @ (yv - p)
        step = np.linalg.solve(H, gvec)
        beta += step
        if abs(step).max() < 1e-8:
            break
    cov = np.linalg.inv(H)
    se = np.sqrt(np.diag(cov))
    names = ["const", "taken", "log(own/enemy length)", "round/100", "own queen alive"]
    for i, nme in enumerate(names):
        P("   %-24s %+.2f  (se %.2f)" % (nme, beta[i], se[i]))
    # average marginal effect of 'taken' on the not-taken rows
    A1 = A.copy()
    A0 = A.copy()
    A1[:, 1] = 1
    A0[:, 1] = 0
    mask = A[:, 1] == 0
    p1 = 1 / (1 + np.exp(-(A1 @ beta)))
    p0 = 1 / (1 + np.exp(-(A0 @ beta)))
    eff = (p1 - p0)[mask].mean()
    # delta-method-free rough interval: move beta_taken by +-1.28 se
    b_lo, b_hi = beta.copy(), beta.copy()
    b_lo[1] -= 1.2816 * se[1]
    b_hi[1] += 1.2816 * se[1]
    e_lo = (1 / (1 + np.exp(-(A1 @ b_lo))) - p0)[mask].mean()
    e_hi = (1 / (1 + np.exp(-(A1 @ b_hi))) - p0)[mask].mean()
    P("   average effect of 'taken' on the win chance of the NOT-taken games: %+.1f points [80%%: %+.1f to %+.1f], n not taken = %d"
      % (100 * eff, 100 * e_lo, 100 * e_hi, int(mask.sum())))


groups = [
    ("meow, all 401 games", lambda g, s: g[s] == X.ME),
    ("meow, live bot", lambda g, s: g[s] == X.ME and X.build(g) == "live"),
    ("forgot", lambda g, s: g[s] == X.FORGOT),
    ("Vibing++", lambda g, s: g[s] == X.VIB),
    ("SSS", lambda g, s: g[s] == X.SSS),
    ("our opponents (on our queen)", lambda g, s: g[X.other(s)] == X.ME),
    ("every other team rated 2000+ (not us, not the top three), playing the top three or us",
     lambda g, s: g[s] not in (X.ME,) + X.TOP3 and g[s + "e"] >= 2000),
]
allrows = {}
for label, pred in groups:
    rows = first_rows(pred)
    allrows[label] = rows
    show(label, rows)
    if len(rows) >= 60 and 5 <= sum(r["taken"] for r in rows) <= len(rows) - 5:
        logit(rows)

P("\n== 3. Pooled over every team with variation (meow, forgot, the other 2000+ teams), with a team term")
pool = allrows["meow, all 401 games"] + allrows["forgot"] + allrows[groups[-1][0]]
show("pooled: meow + forgot + other 2000+ teams", pool)
logit(pool, with_team=True)

P("\n== 4. forgot by the length of the attacker at the first chance (its long dragons mostly pass)")
fr = allrows["forgot"]
for lab, f in (("2-3", lambda L: L <= 3), ("4", lambda L: L == 4), ("5-12", lambda L: L >= 5)):
    rs = [r for r in fr if f(r["L"])]
    P("  attacker %-5s n=%-4d taken %-16s won %-16s her queen dead at end %s" % (
        lab, len(rs), X.frac(sum(r["taken"] for r in rs), len(rs)), X.frac(sum(r["win"] for r in rs), len(rs)),
        X.pct(sum(r["qdead_end"] for r in rs), len(rs))))
    for tk in (True, False):
        r2 = [r for r in rs if r["taken"] == tk]
        P("      %-10s n=%-4d won %-16s median round %s  median ratio %s" % (
            "taken" if tk else "not taken", len(r2), X.frac(sum(r["win"] for r in r2), len(r2)),
            sorted(r["c"]["r"] for r in r2)[len(r2) // 2] if r2 else "-",
            ("%.2f" % sorted(r["ratio"] for r in r2)[len(r2) // 2]) if r2 else "-"))
out.close()
