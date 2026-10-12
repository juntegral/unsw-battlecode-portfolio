#!/usr/bin/env python3
"""Loader for walk 1 (y_out/w1): one record per game-side of interest.

Groups: 'meow' (our 401 games; build live/test), 'opp' (the other side of those 401), 'Vibing++', 'SSS', 'forgot'
(their game-sides against 2000+ teams, Schooltime out). A top-three game against us appears in 'opp' AND under the
top team's own name; tables never add those two groups together.
"""
import json
import os

import y_lib as Y

SN = ("units", "total", "lid", "L", "second", "P", "Ploc", "nloc", "qa", "qlen")
IX = {k: i for i, k in enumerate(SN)}


def load_w1():
    games = {g["game_id"]: g for g in Y.load_games()}
    out = {}
    d = os.path.join(Y.OUT, "w1")
    for f in os.listdir(d):
        if f.endswith(".json"):
            with open(os.path.join(d, f)) as fh:
                w = json.load(fh)
            w["g"] = games[w["gid"]]
            out[w["gid"]] = w
    return out


def sides(w1):
    """Yield records: dict(gid, w, team, group, side, oside, oteam, big, build, won, race, ...)."""
    recs = []
    for gid, w in w1.items():
        g = w["g"]
        for team, side in Y.study_sides(g):
            o = Y.opp(side)
            base = dict(gid=gid, w=w, map=g["map"], cells=int(g["cells"]), big=Y.is_big(g), rounds=w["rounds"],
                        battle=g["battle_id"])
            end = w["snap"]["end"]
            race = (w["rounds"] == 500 and end["A"][IX["qa"]] == 0 and end["B"][IX["qa"]] == 0)
            r = dict(base, team=team, group="meow" if team == Y.ME else Y.TOP[team], side=side, oside=o,
                     oteam=g["team%sId" % o], oname=g["team%sName" % o], build=Y.build_of(g) if team == Y.ME else "",
                     won=(w["winner"] == side), race=race)
            recs.append(r)
            if team == Y.ME:
                recs.append(dict(base, team=g["team%sId" % o], group="opp", side=o, oside=side, oteam=Y.ME,
                                 oname="meow", build=Y.build_of(g), won=(w["winner"] == o), race=race))
    return recs


def snap(rec, rnd, key, own=True):
    s = rec["w"]["snap"].get(str(rnd))
    if s is None:
        return None
    return s[rec["side"] if own else rec["oside"]][IX[key]]


def ratio(rec, rnd, key):
    a, b = snap(rec, rnd, key, True), snap(rec, rnd, key, False)
    if a is None or b is None or b == 0:
        return None
    return a / b


def lineage(w, final_id):
    """List of (id, from_round) going back in time: the final dragon and its ancestors through splits."""
    chain = []
    cur = final_id
    born = w["born"]
    while True:
        b = born.get(str(cur))
        chain.append((cur, b[0] if b else -1))
        if not b:
            break
        cur = b[1]
    return chain  # newest first


def lineage_at(chain, rnd):
    """Id of the lineage member alive as 'the lineage' at round rnd (a child takes over from its birth round on)."""
    for did, frm in chain:
        if rnd >= frm:
            return did
    return chain[-1][0]
