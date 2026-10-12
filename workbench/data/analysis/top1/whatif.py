#!/usr/bin/env python3
"""What-if for the queen-hunt hypothesis on OUR games (opp elo >= 2000, sealed map excluded), by map size.

For every round-500 loss with their queen alive: would we have won if their queen had died and nothing else changed?
(ours dead -> compare our longest with their longest non-queen dragon; ours alive -> queen rule gives us the game.)
Also: how did we do in the games where their queen WAS dead at the end (the state the kill would create)?
"""
import glob
import json
from collections import Counter, defaultdict

SEALED = {"Schooltime"}
tab = defaultdict(Counter)
detail = []
for f in glob.glob("q/*.json"):
    d = json.load(open(f))
    if d["map"] in SEALED:
        continue
    for s in "AB":
        o = "B" if s == "A" else "A"
        if d["sides"][s]["team"] != 1119 or (d["sides"][o]["elo"] or 0) < 2000:
            continue
        c = d["w"] * d["h"]
        sz = "small" if c <= 700 else "medium" if c <= 1500 else "large"
        me, op = d["sides"][s], d["sides"][o]
        t = tab[sz]
        t["games"] += 1
        win = d["winner"] == s
        t["wins"] += win
        if d["end_type"] == "wipe-out":
            t["wipe-outs"] += 1
            continue
        mq, oq = me["final"]["queen"], op["final"]["queen"]
        if oq:
            t["r500, their queen alive"] += 1
            t["r500, their queen alive, we won"] += win
            if not win:
                op_long, op_second = op["final"]["longest"], op["per"]["second"][-1]
                op_noq = op_second if oq == op_long else op_long
                flip = True if mq else me["final"]["longest"] > op_noq
                t["  ... loss that flips if she dies"] += flip
                t["  ... of those, our queen was alive"] += bool(mq)
                detail.append((sz, d["map"], d["game_id"], mq, oq, me["final"]["longest"], op_long, op_second, flip))
        else:
            t["r500, their queen dead"] += 1
            t["r500, their queen dead, we won"] += win
for sz in ("small", "medium", "large"):
    print(sz, dict(tab[sz]))
tot = Counter()
for t in tab.values():
    tot.update(t)
print("all", dict(tot))
print("\nflip detail (size, map, game, our queen, their queen, our longest, their longest, their second, flips):")
by = Counter()
for row in sorted(detail):
    by[(row[1], row[-1])] += 1
print({f"{k[0]} {'flip' if k[1] else 'no'}": v for k, v in sorted(by.items())})
