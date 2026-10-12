#!/usr/bin/env python3
"""Markdown table of the games read closely for deep-read-5.md (section 3): id, map, cells, run, side, opponent, result,
total length and longest dragon at rounds 300 / 400 / end for both sides, potential at 400 and the end, when the two
queens died. Reads e_out/w4 and games.csv. Output: e_out/games_read.md"""
import json
import os

import e_lib as E

OURS_LOST = [1027819, 1044512, 1063241, 1068052, 1058146, 1027971, 1045202, 1058858, 1063251, 1063682, 1029033, 1045374, 1058363, 1029032]
OURS_LEVEL_WON = [1023828, 1053031, 1063672, 1067916]
OURS_BIG_WON = [1053032, 1059086, 1053383, 1063675]
TOP = [(91, 1046530), (91, 1054770), (91, 1051292), (306, 1069890), (306, 1055103), (306, 1061101), (264, 1046978), (264, 1058793)]
G = {g["gid"]: g for g in E.load_games()}


def line(n, gid, team, kind):
    g = G[gid]
    d = json.load(open(os.path.join(E.HERE, "e_out", "w4", "%d.json" % gid)))
    S = "A" if g["A"] == team else "B"
    O = E.other(S)
    s, o = d["sides"][S], d["sides"][O]

    def at(r):
        a, b = s["tl"][r // 5], o["tl"][r // 5]
        return "%d : %d" % (a[2], b[2]), "%d : %d" % (a[3], b[3]), "%d : %d" % (a[3] + a[12], b[3] + b[12])
    t3, l3, p3 = at(300)
    t4, l4, p4 = at(400)
    fs, fo = s["final"], o["final"]
    qd = lambda x: ("r%d" % x["qdeath"][0]) if x["qdeath"] else "alive"
    return "| %d | %d | %s | %d | %s | %s | %s | %s (%d) | %s | %s / %s / %d : %d | %s / %s / %d : %d | %s / %s / %d : %d | %d : %d | %s, %s |" % (
        n, gid, g["map"], g["cells"], g["set"] if team == E.ME else "ladder", kind, E.NAMES.get(team, str(team)), g[O + "n"][:16], g[O + "e"],
        "won" if d["winner"] == S else "lost", t3, t4, fs["total"], fo["total"], l3, l4, fs["top"][0][0], fo["top"][0][0],
        p3, p4, fs["top"][0][0] + fs["pot"], fo["top"][0][0] + fo["pot"], fs["units"], fo["units"], qd(s), qd(o))


out = ["| # | game | map | cells | run | why read | read for | opponent (elo) | result | total length at 300 / 400 / end, own : enemy | longest at 300 / 400 / end | "
       "potential at 300 / 400 / end | units at the end | queens died (own, enemy) |", "|" + "---|" * 14]
n = 0
for gid in OURS_LOST:
    n += 1
    out.append(line(n, gid, E.ME, "lost with level or more total length at round 400"))
for gid in OURS_LEVEL_WON:
    n += 1
    out.append(line(n, gid, E.ME, "level race we won"))
for gid in OURS_BIG_WON:
    n += 1
    out.append(line(n, gid, E.ME, "big map, won from behind"))
for team, gid in TOP:
    n += 1
    out.append(line(n, gid, team, "top-team win of a level race, small map"))
open(os.path.join(E.HERE, "e_out", "games_read.md"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
