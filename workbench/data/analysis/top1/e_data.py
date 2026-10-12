#!/usr/bin/env python3
"""Loader for the per-game files of e_walk.py (e_out/w/<gid>.json) and the groups used in every A5 table.

rows() returns one record per (game, side) for every side of every walked game:
  gid, map, cells, big (over 1,200 cells), set (battle id), build ('live' or the test build), S (side letter), team, opp,
  opp_elo, study (this side passes the study filter: opponent 2000+, no Schooltime), won, rounds, r500, qa (own queen alive
  at the end), eqa (enemy queen alive at the end), bd (round-500 game with both queens dead), s (own side data), o (the
  other side's data), ratio(r) = own / enemy total length at round r.
groups(rec) names the tables' columns a record belongs to.
"""
import json
import os
import pickle

import e_lib as E

W = os.path.join(E.HERE, "e_out", "w4")
PK = os.path.join(E.HERE, "e_out", "w4.pickle")
ORDER = ("meow live", "meow test", "meow", "opp", "forgot", "SSS", "Vibing++", "top3")


class Rec(dict):
    __getattr__ = dict.get

    def tl(self, r, own=True):
        """Timeline row at round r (multiple of 5) for the own or the other side; None if the game was over."""
        t = (self["s"] if own else self["o"])["tl"]
        i = r // 5
        return t[i] if i < len(t) else None

    def ratio(self, r):
        a, b = self.tl(r), self.tl(r, False)
        if not a or not b or not b[2]:
            return None
        return a[2] / b[2]

    def lin_len(self, r, own=True):
        lin = (self["s"] if own else self["o"])["lin"]
        if not lin:
            return None
        i = r // 5
        return lin["curve"][i] if i < len(lin["curve"]) else None


def load_all(cache=True):
    metas = {g["gid"]: g for g in E.load_games()}
    files = sorted(f for f in os.listdir(W) if f.endswith(".json"))
    if cache and os.path.exists(PK):
        data = pickle.load(open(PK, "rb"))
        if len(data) == len(files):
            return data, metas
    data = {}
    for f in files:
        try:
            d = json.load(open(os.path.join(W, f)))
        except Exception:  # noqa: BLE001  (a file being written right now)
            continue
        data[d["gid"]] = d
    if cache:
        pickle.dump(data, open(PK, "wb"))
    return data, metas


def rows(cache=True):
    data, metas = load_all(cache)
    out = []
    for gid, d in data.items():
        g = metas[gid]
        r500 = d["rounds"] >= 500
        for S in "AB":
            O = E.other(S)
            s, o = d["sides"][S], d["sides"][O]
            qa, eqa = s["final"]["queen"] > 0, o["final"]["queen"] > 0
            out.append(Rec(gid=gid, map=d["map"], cells=d["cells"], big=d["cells"] > 1200, set=d["set"], build=E.build(g),
                           S=S, team=g[S], opp=g[O], opp_elo=g[O + "e"], study=E.in_study(g, S), won=d["winner"] == S,
                           rounds=d["rounds"], r500=r500, qa=qa, eqa=eqa, bd=r500 and not qa and not eqa, s=s, o=o, d=d,
                           me=d["me"] == S))
    return out


def groups(rec):
    """Column names this side belongs to."""
    out = []
    t = rec["team"]
    if rec["study"]:
        if t == E.ME:
            out += ["meow", "meow live" if rec["build"] == "live" else "meow test"]
        if t == E.FORGOT:
            out += ["forgot", "top3"]
        if t == E.SSS:
            out += ["SSS", "top3"]
        if t == E.VIB:
            out += ["Vibing++", "top3"]
        if t in E.TOP3 and rec["opp"] in (E.T4, E.WHQ):
            out.append("top3 vs t4/WHQ")
    if rec["opp"] == E.ME and rec["opp_elo"] is not None:
        # the other side of one of OUR study games (meow's side must pass the filter: this side is rated 2000+)
        g_elo_ok = rec["d"][rec["S"] + "e"] >= 2000 and rec["map"] != "Schooltime"
        if g_elo_ok:
            out.append("opp")
            if t == E.T4:
                out.append("test4 (vs us)")
            elif t == E.WHQ:
                out.append("WHQ (vs us)")
    if t == E.T4 and rec["opp"] in E.TOP3 and rec["map"] != "Schooltime":
        out.append("test4 (vs top3)")
    if t == E.WHQ and rec["opp"] in E.TOP3 and rec["map"] != "Schooltime":
        out.append("WHQ (vs top3)")
    return out


def band400(rec):
    x = rec.ratio(400)
    if x is None:
        return None
    return "under 0.5" if x < 0.5 else "0.5-0.8" if x < 0.8 else "0.8-1.25" if x <= 1.25 else "over 1.25"


BANDS = ("under 0.5", "0.5-0.8", "0.8-1.25", "over 1.25")


def med(v, nd=0):
    v = sorted(x for x in v if x is not None)
    n = len(v)
    if not n:
        return "-"
    m = v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2
    return ("%.*f" % (nd, m)) if nd else ("%d" % round(m) if abs(m - round(m)) < 1e-9 else "%.1f" % m)


def mean(v, nd=1):
    v = [x for x in v if x is not None]
    return ("%.*f" % (nd, sum(v) / len(v))) if v else "-"


def pct(k, n, nd=0):
    return "-" if not n else "%.*f%%" % (nd, 100.0 * k / n)


def frac(k, n):
    return "%d of %d" % (k, n) + (" = %s" % pct(k, n) if n else "")


class Out:
    """print and write to a file at once."""

    def __init__(self, name):
        self.f = open(os.path.join(E.HERE, "e_out", name), "w")

    def __call__(self, *a):
        s = " ".join(str(x) for x in a)
        print(s)
        self.f.write(s + "\n")
