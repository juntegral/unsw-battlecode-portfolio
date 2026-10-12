#!/usr/bin/env python3
"""One line per game for a list of game ids, read from the lead's q/<gid>.json and games.csv:
map, cells, run, side, opponent, result, total and longest at rounds 300 / 400 / end for both sides, queen deaths.
Usage: python3 e_list.py <team_id> id,id,...        (team_id = whose side to print first)
       python3 e_list.py pick <team_id> [big|small] [level|behind|ahead] [W|L]   (round-500 games, both queens dead)
"""
import json
import sys

import e_lib as E

G = {g["gid"]: g for g in E.load_games()}


def q(gid):
    return json.load(open("%s/q/%d.json" % (E.HERE, gid)))


def at(side, r):
    per = side["per"]
    i = min(r, len(per["total"]) - 1)
    return per["units"][i], per["total"][i], per["longest"][i]


def line(gid, team):
    g = G[gid]
    d = q(gid)
    S = "A" if g["A"] == team else "B"
    O = E.other(S)
    s, o = d["sides"][S], d["sides"][O]
    n = len(s["per"]["total"])
    txt = "%d | %s | %d | %s | %s | %s (%d) | %s by %s |" % (
        gid, g["map"], g["cells"], g["set"] if team == E.ME else "-", S, g[O + "n"][:16], g[O + "e"], "W" if g["winner"] == S else "L", g["end_type"])
    for r in (300, 400):
        if r < n:
            a, b = at(s, r), at(o, r)
            txt += " r%d total %d:%d longest %d:%d units %d:%d |" % (r, a[1], b[1], a[2], b[2], a[0], b[0])
    txt += " end total %d:%d longest %d:%d units %d:%d | queens died: own %s, hers %s" % (
        s["final"]["total"], o["final"]["total"], s["final"]["longest"], o["final"]["longest"], s["final"]["units"], o["final"]["units"],
        ("r%d %s" % (s["qdeath"]["round"], s["qdeath"]["reason"])) if s["qdeath"] else "alive",
        ("r%d %s" % (o["qdeath"]["round"], o["qdeath"]["reason"])) if o["qdeath"] else "alive")
    return txt


if __name__ == "__main__":
    if sys.argv[1] == "pick":
        team = int(sys.argv[2])
        cls = sys.argv[3] if len(sys.argv) > 3 else None
        band = sys.argv[4] if len(sys.argv) > 4 else None
        res = sys.argv[5] if len(sys.argv) > 5 else None
        for g in E.load_games():
            for S in "AB":
                if g[S] != team or not E.in_study(g, S) or g["rounds"] < 500:
                    continue
                d = q(g["gid"])
                s, o = d["sides"][S], d["sides"][E.other(S)]
                if s["final"]["queen"] or o["final"]["queen"]:
                    continue
                if cls and (g["cells"] > 1200) != (cls == "big"):
                    continue
                a, b = at(s, 400), at(o, 400)
                ratio = a[1] / max(1, b[1])
                bn = "behind" if ratio < 0.8 else "level" if ratio <= 1.25 else "ahead"
                if band and bn != band:
                    continue
                if res and (g["winner"] == S) != (res == "W"):
                    continue
                print(line(g["gid"], team))
    else:
        team = int(sys.argv[1])
        for x in sys.argv[2].split(","):
            print(line(int(x), team))
