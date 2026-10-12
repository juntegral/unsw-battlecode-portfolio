#!/usr/bin/env python3
"""Turn-level examples: our round-500 losses with their queen alive in which we had legal ram chances.
Prints game, map, opponent, number of chances (all / at most 2 paid steps by a non-longest dragon), the cheap ones
(round, dragon id, length, steps), whether her death would flip the game."""
import glob
import json

rows = []
for f in glob.glob("q/*.json"):
    d = json.load(open(f))
    if d["map"] == "Schooltime" or d["end_type"] == "wipe-out":
        continue
    for s in "AB":
        o = "B" if s == "A" else "A"
        if d["sides"][s]["team"] != 1119 or (d["sides"][o]["elo"] or 0) < 2000 or d["winner"] == s:
            continue
        me, op = d["sides"][s], d["sides"][o]
        oq = op["final"]["queen"]
        if not oq:
            continue
        ch = [c for c in json.load(open(f"q3/{d['game_id']}.json"))["chances"] if c[1] == s]
        cheap = [c for c in ch if max(0, c[4] - (-(-c[3] // 4))) <= 2 and not c[7]]
        if not ch:
            continue
        op_long, op_second = op["final"]["longest"], op["per"]["second"][-1]
        op_noq = op_second if oq == op_long else op_long
        flip = bool(me["final"]["queen"]) or me["final"]["longest"] > op_noq
        rows.append((len(cheap), len(ch), d["game_id"], d["map"], op["name"][:14], flip, oq, me["final"]["longest"], op_noq,
                     [(c[0], c[2], c[3], c[4]) for c in cheap[:8]]))
rows.sort(reverse=True)
for r in rows:
    print(r)
