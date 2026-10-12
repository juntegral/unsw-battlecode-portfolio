#!/usr/bin/env python3
"""Shared helpers for the second red-team round (sub-session C2). My own code; uses only lib.py and games.csv.

Game sets (the study's filter): opponents rated 2000 or more, map Schooltime left out.
- ours: the 401 games of team 1119 (live = ladder downloads and "-old" halves; test = "-new" halves)
- top:  the games of 306 (Vibing++), 91 (SSS), 264 (forgot to mention) against 2000+ teams
"""
import csv
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "y_out")
ME = "1119"
TOP = {"306": "Vibing++", "91": "SSS", "264": "forgot"}
T4, WHQ = "19", "87"
BIG_CELLS = 1200


def load_games():
    rows = list(csv.DictReader(open(os.path.join(HERE, "games.csv"))))
    return rows


def elo(g, side):
    try:
        return float(g["team%sElo" % side])
    except (ValueError, KeyError):
        return 0.0


def side_of(g, team):
    if g["teamAId"] == team:
        return "A"
    if g["teamBId"] == team:
        return "B"
    return None


def opp(side):
    return "B" if side == "A" else "A"


def study_sides(g):
    """List of (team_id, side) of study teams in this game that pass the filter (opponent 2000+, not Schooltime)."""
    out = []
    if g["map"] == "Schooltime":
        return out
    for team in [ME] + list(TOP):
        s = side_of(g, team)
        if s is None:
            continue
        if elo(g, opp(s)) >= 2000:
            out.append((team, s))
    return out


def build_of(g):
    """'live' or 'test' for our games, by battle_id."""
    b = g["battle_id"]
    if b.startswith("dl-") or b.endswith("-old"):
        return "live"
    if b.endswith("-new"):
        return "test"
    return "live"


def is_big(g):
    return int(g["cells"]) > BIG_CELLS


def out_path(*parts):
    p = os.path.join(OUT, *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def dump(obj, *parts):
    p = out_path(*parts)
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, separators=(",", ":"))
    os.replace(tmp, p)


def load(*parts):
    with open(os.path.join(OUT, *parts)) as f:
        return json.load(f)


def med(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def pct(a, b):
    return "%d of %d = %.0f%%" % (a, b, 100.0 * a / b) if b else "0 of 0"


def fmt(x, nd=1):
    if x is None:
        return "-"
    return ("%." + str(nd) + "f") % x


def _solve(A, b):
    """Solve A x = b (small dense system), returns x and the inverse of A."""
    n = len(A)
    M = [list(A[i]) + [1.0 if i == j else 0.0 for j in range(n)] + [b[i]] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-12:
            raise ValueError("singular")
        M[c], M[p] = M[p], M[c]
        d = M[c][c]
        M[c] = [v / d for v in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0.0:
                f = M[r][c]
                M[r] = [v - f * w for v, w in zip(M[r], M[c])]
    x = [M[i][-1] for i in range(n)]
    inv = [M[i][n:2 * n] for i in range(n)]
    return x, inv


def sigmoid(z):
    import math
    if z > 35:
        return 1.0
    if z < -35:
        return 0.0
    return 1.0 / (1.0 + math.exp(-z))


def logit_fit(X, y, ridge=1e-6, iters=60):
    """Plain logistic regression by Newton steps. X: list of rows (include a 1.0 column yourself), y: 0/1.
    Returns (beta, cov, loglik)."""
    import math
    n, k = len(X), len(X[0])
    beta = [0.0] * k
    for _ in range(iters):
        g = [0.0] * k
        H = [[ridge if i == j else 0.0 for j in range(k)] for i in range(k)]
        for row, yi in zip(X, y):
            p = sigmoid(sum(b * v for b, v in zip(beta, row)))
            w = p * (1 - p)
            for i in range(k):
                g[i] += (yi - p) * row[i]
                ri = row[i] * w
                Hi = H[i]
                for j in range(k):
                    Hi[j] += ri * row[j]
        for i in range(k):
            g[i] -= ridge * beta[i]
        step, inv = _solve(H, g)
        beta = [b + s for b, s in zip(beta, step)]
        if max(abs(s) for s in step) < 1e-9:
            break
    ll = 0.0
    for row, yi in zip(X, y):
        p = min(1 - 1e-12, max(1e-12, sigmoid(sum(b * v for b, v in zip(beta, row)))))
        ll += math.log(p) if yi else math.log(1 - p)
    return beta, inv, ll


def wilson(k, n, z=1.2816):
    """80% Wilson interval for a share."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))
