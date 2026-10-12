#!/usr/bin/env python3
"""Shared loader for the red-team scripts (own code). Reads x_out/games.json and the per-game files of a walker."""
import json
import math
import os
import pickle

sys_dont = True
ME, VIB, SSS, FORGOT = 1119, 306, 91, 264
TOP3 = (VIB, SSS, FORGOT)
T4, WHQ, DEV1 = 19, 87, 545
NAMES = {ME: "meow", VIB: "Vibing++", SSS: "SSS", FORGOT: "forgot", T4: "test4", WHQ: "WeHaveQuizzes", DEV1: "dev test 1"}
LIVE_SETS = ("dl-20261003", "dl-20261004")


def games(with_dir=None, cache=True):
    """All games (csv + extra smoke). with_dir: attach the walker's per-game JSON as g['d']."""
    gs = json.load(open("x_out/games.json"))
    if with_dir:
        pk = "x_out/%s.pickle" % with_dir
        data = None
        if cache and os.path.exists(pk):
            data = pickle.load(open(pk, "rb"))
            if len(data) < len(gs) - 5:
                data = None
        if data is None:
            data = {}
            for g in gs:
                p = "x_out/%s/%d.json" % (with_dir, g["gid"])
                if os.path.exists(p):
                    data[g["gid"]] = json.load(open(p))
            if cache:
                pickle.dump(data, open(pk, "wb"))
        for g in gs:
            g["d"] = data.get(g["gid"])
    return gs


def side_of(g, team):
    return "A" if g["A"] == team else ("B" if g["B"] == team else None)


def other(side):
    return "B" if side == "A" else "A"


def opp(g, side):
    o = other(side)
    return g[o], g[o + "n"], g[o + "e"]


def in_study(g, side):
    """The study's filter: opponent rated 2000+, map Schooltime left out."""
    return opp(g, side)[2] >= 2000 and g["map"] != "Schooltime"


def is_csv(g):
    return g["src"] == "csv"


def build(g):
    """'live' for ladder downloads and the -old halves of smoke pairs, else the candidate's name."""
    s = g["set"]
    if s in LIVE_SETS or s.endswith("-old"):
        return "live"
    for k in ("-test-new", "-dev1b-new", "-dev1-new", "-new"):
        if s.endswith(k):
            return s[: -len(k)]
    return s


def won(g, side):
    return g["winner"] == side


def wilson(k, n, z=1.2816):
    """80% Wilson interval by default (z = 1.2816)."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, mid - half), min(1.0, mid + half))


def pct(k, n, d=0):
    return "-" if n == 0 else ("%.*f%%" % (d, 100.0 * k / n))


def frac(k, n, d=0):
    return "%d of %d = %s" % (k, n, pct(k, n, d)) if n else "0 of 0"


def band(ratio):
    return 0 if ratio < 0.67 else 1 if ratio < 1.0 else 2 if ratio < 1.5 else 3


BAND_NAMES = ("<0.67", "0.67-1", "1-1.5", ">1.5")


def tl_at(d, r):
    """Timeline row at round r (multiple of 10), or the last one before it: [r, A*5, B*5]."""
    tl = d["timeline"]
    i = min(len(tl) - 1, r // 10)
    return tl[i] if tl and tl[i][0] <= r else None


def stats_at(d, r, side):
    """(units, total, longest, longest non-queen, queen length) of `side` at round r, None if the game ended before."""
    tl = d["timeline"]
    i = r // 10
    if i >= len(tl):
        return None
    row = tl[i]
    return row[1:6] if side == "A" else row[6:11]
