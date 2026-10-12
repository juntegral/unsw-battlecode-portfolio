#!/usr/bin/env python3
"""What the missed in-view rams cost us (q3v2, our games, opp elo >= 2000, sealed map excluded).

A "missed game" = we had at least one in-view chance (free path to the enemy queen's head within reach, her head inside
the attacker's 7x7 square at its turn) and never rammed her in that game.
1. What those games became; how many flip if she had died at the first missed chance and nothing else changed.
2. The same split by the cost of the cheapest missed chance (paid steps) and by whether the attacker was our longest.
3. Per map.
4. When the first missed chance came (round) and what state the game was in.
"""
import glob
import json
import statistics
from collections import Counter, defaultdict

SEALED = {"Schooltime"}
rows = []
tot = Counter()
for f in glob.glob("q/*.json"):
    d = json.load(open(f))
    if d["map"] in SEALED:
        continue
    for s in "AB":
        o = "B" if s == "A" else "A"
        if d["sides"][s]["team"] != 1119 or (d["sides"][o]["elo"] or 0) < 2000:
            continue
        tot["games"] += 1
        win = d["winner"] == s
        tot["wins"] += win
        ch = [c for c in json.load(open(f"q3v2/{d['game_id']}.json"))["chances"] if c[1] == s and c[9]]
        qd = d["sides"][o]["qdeath"]
        killed = bool(qd and qd["reason"] == "headon" and qd["killer"] and qd["killer"]["team"] == s)
        tot["games with an in-view chance"] += bool(ch)
        tot["we rammed her"] += killed
        if not ch or killed:
            continue
        me, op = d["sides"][s], d["sides"][o]
        oq, mq = op["final"]["queen"], me["final"]["queen"]
        if d["end_type"] == "wipe-out":
            state = "wipe-out " + ("W" if win else "L")
            flip = False
        else:
            state = f"r500 her {'alive' if oq else 'dead'} " + ("W" if win else "L")
            flip = False
            if oq and not win:
                op_long, op_second = op["final"]["longest"], op["per"]["second"][-1]
                op_noq = op_second if oq == op_long else op_long
                flip = bool(mq) or me["final"]["longest"] > op_noq
        cheapest = min(max(0, c[4] - (-(-c[3] // 4))) for c in ch)
        nonlong = [c for c in ch if not c[7]]
        first = min(c[0] for c in ch)
        rows.append(dict(gid=d["game_id"], map=d["map"], state=state, flip=flip, n=len(ch), cheapest=cheapest,
                         nonlong=bool(nonlong), first=first, opp=op["name"][:14], cells=d["w"] * d["h"],
                         lens=sorted({c[3] for c in ch})))
print(dict(tot))
print("missed games:", len(rows))
print("  became:", dict(Counter(r["state"] for r in rows)))
print("  flips if she had died:", sum(r["flip"] for r in rows))
print("  by cheapest missed chance (paid steps): games / r500-her-alive losses / flips")
for k in (0, 1, 2, 3, 4):
    sub = [r for r in rows if (r["cheapest"] == k if k < 4 else r["cheapest"] >= 4)]
    print(f"    {k}{'+' if k == 4 else ''} paid: {len(sub):3d} / {sum(r['state'] == 'r500 her alive L' for r in sub):2d} / {sum(r['flip'] for r in sub)}")
sub = [r for r in rows if not r["nonlong"]]
print(f"  only our longest dragon had the chance: {len(sub)} games, flips {sum(r['flip'] for r in sub)}")
print("  by map class:", {k: (sum(1 for r in rows if (r['cells'] > 1200) == b), sum(r['flip'] for r in rows if (r['cells'] > 1200) == b))
                          for k, b in (("<=1200 cells", False), (">1200 cells", True))})
bm = defaultdict(lambda: [0, 0, 0])
for r in rows:
    bm[r["map"]][0] += 1
    bm[r["map"]][1] += r["state"] == "r500 her alive L"
    bm[r["map"]][2] += r["flip"]
print("  per map (missed games, r500 losses with her alive, flips):", {m: tuple(v) for m, v in sorted(bm.items())})
print("  first missed chance, round: median", statistics.median(r["first"] for r in rows),
      " before r150:", sum(r["first"] < 150 for r in rows), " r150-299:", sum(150 <= r["first"] < 300 for r in rows), " r300+:", sum(r["first"] >= 300 for r in rows))
print("  flip games:")
for r in sorted(rows, key=lambda r: r["gid"]):
    if r["flip"]:
        print("   ", r["gid"], r["map"], r["opp"], "chances", r["n"], "cheapest paid", r["cheapest"], "first round", r["first"], "attacker lengths", r["lens"])
# wipe-out losses: was her death before our wipe-out relevant? count wipe-out L where she alone or few remained - not estimated
