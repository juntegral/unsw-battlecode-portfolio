#!/usr/bin/env python3
"""Deaths by choice of one side of one game between two rounds, one line each, and a summary: how many died within 1, 2,
3 path steps of an own dragon at least twice as long ("the dragon fed"), how many of those next to the team's longest,
and where the pearls went. Reads e_out/w4/<gid>.json.
Usage: python3 e_feed.py <game_id> <A|B|me|opp> <from_round> <to_round> [--list]"""
import json
import os
import sys

import e_lib as E

RE = ("wall", "self", "body", "headon", "noaction", "other")


def main():
    gid, side, r1, r2 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    d = json.load(open(os.path.join(E.HERE, "e_out", "w4", "%s.json" % gid)))
    if side == "me":
        side = d["me"]
    elif side == "opp":
        side = E.other(d["me"])
    s = d["sides"][side]
    me = d["me"] == side
    DI = {k: i for i, k in enumerate(d["dcol"])}
    rows = [x for x in s["deaths"] if r1 <= x[0] <= r2 and (x[DI["cls"]] == 2 or (me and x[DI["reason"]] == 4 and x[DI["akind"]] == 2))]
    print("game %s side %s = %s, deaths by choice r%d-%d: %d, length %d" % (gid, side, d[side + "n"], r1, r2, len(rows), sum(x[2] for x in rows)))
    hist = {}
    nlead = nfed = 0
    p = [0, 0, 0, 0, 0, 0]
    for x in rows:
        td = x[DI["tdist"]]
        key = td if 0 <= td <= 3 else ("4-8" if td > 3 else "none")
        hist[key] = hist.get(key, 0) + 1
        if 0 <= td <= 3:
            nfed += 1
            if x[DI["tid"]] == x[DI["lid"]]:
                nlead += 1
        p[0] += x[DI["drop"]]
        for i, k in enumerate(("e_t", "e_l", "e_q", "e_o", "e_e")):
            p[i + 1] += x[DI[k]]
        if "--list" in sys.argv:
            print("   r%d #%d L%d %s at (%d,%d) | fed #%d L%d d%d | longest #%d L%d m%d | enemy head %d | pearls %d: %d/%d/%d/%d/%d" % (
                x[0], x[1], x[2], RE[x[DI["reason"]]], x[DI["x"]], x[DI["y"]], x[DI["tid"]], x[DI["tlen"]], td, x[DI["lid"]], x[DI["llen"]], x[DI["lmanh"]],
                x[DI["emanh"]], x[DI["drop"]], x[DI["e_t"]], x[DI["e_l"]], x[DI["e_q"]], x[DI["e_o"]], x[DI["e_e"]]))
    print("   path steps to an own dragon twice as long: " + ", ".join("%s: %d" % (k, hist[k]) for k in sorted(hist, key=str)))
    print("   within 3 steps of such a dragon: %d; of those, that dragon was the team's longest: %d" % (nfed, nlead))
    print("   pearls dropped %d -> dragon fed %d, longest otherwise %d, queen %d, other own %d, enemy %d, nobody %d" % (
        p[0], p[1], p[2], p[3], p[4], p[5], p[0] - sum(p[1:])))
    reasons = {}
    for x in rows:
        reasons[RE[x[DI["reason"]]]] = reasons.get(RE[x[DI["reason"]]], 0) + 1
    print("   how they died: " + ", ".join("%s %d" % kv for kv in sorted(reasons.items())))


main()
