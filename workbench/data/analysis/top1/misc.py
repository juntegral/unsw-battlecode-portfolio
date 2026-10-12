#!/usr/bin/env python3
"""Smaller questions answered from q/*.json.

A. Do queens park? Share of 25-round windows (queen alive throughout) in which she visits <= 6 / <= 10 different cells.
E. When are enemy queens killed (round histogram of rams on the enemy queen), per team and map size.
F. Missed chances: in our round-500 losses where their queen lived and ours did not, how many rounds was their queen
   inside the one-turn reach of one of our heads, and how close did our small dragons get.
G. Queen survival by map (who survives where), top three pooled vs us.
"""
import glob
import json
import statistics
from collections import Counter, defaultdict

TOP = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}
SEALED = {"Schooltime"}
games = [json.load(open(f)) for f in glob.glob("q/*.json")]


def size(d):
    c = d["w"] * d["h"]
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


def sides(team):
    for d in games:
        for s in "AB":
            o = "B" if s == "A" else "A"
            if d["sides"][s]["team"] == team and (d["sides"][o]["elo"] or 0) >= 2000:
                yield d, s, o


print("=== A. parking: share of 25-round windows with few distinct queen cells (sealed map excluded)")
for team, name in TOP.items():
    for sz in ("small", "medium", "large"):
        n = c6 = c10 = 0
        by_phase = defaultdict(lambda: [0, 0])
        for d, s, o in sides(team):
            if size(d) != sz or d["map"] in SEALED:
                continue
            q = d["sides"][s]["per"]["q"]
            for a in range(25, len(q) - 25, 25):
                w = q[a:a + 25]
                if any(x is None for x in w):
                    continue
                cells = len({(x[0], x[1]) for x in w})
                n += 1
                c6 += cells <= 6
                c10 += cells <= 10
                ph = "r25-150" if a < 150 else "r150-300" if a < 300 else "r300+"
                by_phase[ph][0] += cells <= 10
                by_phase[ph][1] += 1
        if n:
            print(f"{name:9s} {sz:6s} windows={n:5d} <=6 cells: {c6 / n:.3f}  <=10 cells: {c10 / n:.3f}  | "
                  + " ".join(f"{k}: {v[0] / v[1]:.2f} (n{v[1]})" for k, v in sorted(by_phase.items())))

print("\n=== E. round of the ram that killed the ENEMY queen (kills by this team), share of games with a kill by round R")
for team, name in TOP.items():
    for sz in ("small", "medium", "large"):
        n = 0
        rounds = []
        for d, s, o in sides(team):
            if size(d) != sz or d["map"] in SEALED:
                continue
            n += 1
            qd = d["sides"][o]["qdeath"]
            if qd and qd["reason"] == "headon" and qd["killer"] and qd["killer"]["team"] == s:
                rounds.append(qd["round"])
        if n:
            cum = [sum(r < R for r in rounds) / n for R in (100, 200, 300, 400, 500)]
            print(f"{name:9s} {sz:6s} games={n:3d} killed their queen in {len(rounds) / n:.2f}; by r100/200/300/400/500: "
                  + " ".join(f"{c:.2f}" for c in cum) + f"  median round {statistics.median(rounds) if rounds else '-'}")

print("\n=== F. missed chances in OUR round-500 losses with their queen alive and ours dead (sealed map excluded)")
rows = []
for d, s, o in sides(1119):
    if d["map"] in SEALED or d["end_type"] == "wipe-out" or d["winner"] == s:
        continue
    me, op = d["sides"][s], d["sides"][o]
    if me["final"]["queen"] or not op["final"]["queen"]:
        continue
    q = op["per"]["q"]
    exposed = sum(1 for x in q if x and x[9] is not None and x[9] <= 0)
    near3 = sum(1 for x in q if x and x[10] is not None and x[10] <= 3)
    near6 = sum(1 for x in q if x and x[10] is not None and x[10] <= 6)
    seen = sum(1 for x in q if x and x[8] > 0)
    after = sum(1 for r, x in enumerate(q) if x and x[9] is not None and x[9] <= 0 and me["qdeath"] and r > me["qdeath"]["round"])
    rows.append((d["game_id"], d["map"], exposed, near3, near6, seen, after, op["final"]["queen"]))
print("games:", len(rows))
for label, idx in (("rounds their queen was inside one of our heads' one-turn reach", 2), ("rounds one of our small (<=4) heads was within 3 steps of her", 3),
                   ("... within 6 steps", 4), ("rounds one of our heads could SEE her", 5), ("reach-rounds after our own queen had died", 6)):
    v = sorted(r[idx] for r in rows)
    print(f"  {label}: median {statistics.median(v)}, mean {sum(v) / len(v):.1f}, games with zero: {sum(1 for x in v if x == 0)}, games with >= 5: {sum(1 for x in v if x >= 5)}")
print("  per map:", dict(Counter(r[1] for r in rows)))

print("\n=== G. own queen alive at the end, by map (games vs >= 2000): top three pooled | meow")
tab = defaultdict(lambda: [0, 0, 0, 0])
for team in TOP:
    for d, s, o in sides(team):
        k = 2 if team == 1119 else 0
        tab[d["map"]][k] += d["sides"][s]["final"]["queen"] > 0
        tab[d["map"]][k + 1] += 1
for m, v in sorted(tab.items()):
    print(f"  {m:18s} top3 {v[0]:3d}/{v[1]:3d} = {v[0] / max(1, v[1]):.2f}   meow {v[2]:2d}/{v[3]:2d} = {v[2] / max(1, v[3]):.2f}")
