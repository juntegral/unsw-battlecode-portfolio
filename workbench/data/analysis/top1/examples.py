#!/usr/bin/env python3
"""Find replay moments for the card: our round-500 losses where their queen lived, ours was dead, and she was inside the
one-turn reach of one of our heads for many rounds. Prints game, map, her side, rounds in reach, the longest streak of
such rounds, whether her death would flip the game. Reads q/*.json."""
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
        if not op["final"]["queen"]:
            continue
        q = op["per"]["q"]
        inreach = [r for r, x in enumerate(q) if x and x[9] is not None and x[9] <= 0]
        small3 = [r for r, x in enumerate(q) if x and x[10] is not None and x[10] <= 2]
        best = cur = 0
        prev = -5
        start = None
        beststart = None
        for r in inreach:
            if r == prev + 1:
                cur += 1
            else:
                cur = 1
                start = r
            if cur > best:
                best, beststart = cur, start
            prev = r
        op_long, op_second = op["final"]["longest"], op["per"]["second"][-1]
        oq = op["final"]["queen"]
        op_noq = op_second if oq == op_long else op_long
        flip = bool(me["final"]["queen"]) or me["final"]["longest"] > op_noq
        rows.append((len(inreach), d["game_id"], d["map"], o, best, beststart, len(small3), small3[:6], oq, me["final"]["longest"], op_noq, flip,
                     d["sides"][o]["name"][:14]))
rows.sort(reverse=True)
print("reach-rounds | game | map | her side | longest streak (from round) | rounds a small head of ours was within 2 steps (first six) | her final len | our longest | their best non-queen | flips | opponent")
for r in rows[:22]:
    print(r)
