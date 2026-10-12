#!/usr/bin/env python3
"""Turn-level ram chances on the enemy queen (q3/*.json from extract3.py), opp elo >= 2000, sealed map excluded.

A chance = at the start of a non-queen dragon's own turn there is a path of free cells from its head to the enemy
queen's head no longer than its one-turn reach. Taken = it rammed her that turn.
Tables: by attacker team group x attacker length x steps needed; by paid steps needed; by map class; by phase; per game.
"""
import glob
import json
from collections import defaultdict

TEAMS = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}
SEALED = {"Schooltime"}
Q = {}
for f in glob.glob("q/*.json"):
    d = json.load(open(f))
    if d["map"] not in SEALED:
        Q[d["game_id"]] = d
Q3 = {}
for f in glob.glob("q3/*.json"):
    d = json.load(open(f))
    Q3[d["game_id"]] = d


def lc(n):
    return "L2" if n <= 2 else "L3" if n == 3 else "L4" if n == 4 else "L5-9" if n <= 9 else "L10-12"


def rate(t):
    return f"{t[1]:4d}/{t[0]:5d} = {t[1] / t[0]:.3f}" if t[0] else "   -"


by_len = defaultdict(lambda: [0, 0])
by_steps = defaultdict(lambda: [0, 0])
by_paid = defaultdict(lambda: [0, 0])
by_map = defaultdict(lambda: [0, 0])
by_phase = defaultdict(lambda: [0, 0])
by_leader = defaultdict(lambda: [0, 0])
games = defaultdict(lambda: [0, 0, 0, 0, 0])   # games, games with >=1 chance, chances, taken, kills without chance
first = defaultdict(lambda: [0, 0])
for gid, d in Q.items():
    d3 = Q3.get(gid)
    if d3 is None:
        continue
    for s in "AB":
        o = "B" if s == "A" else "A"
        t = d["sides"][s]["team"]
        if t not in TEAMS or (d["sides"][o]["elo"] or 0) < 2000:
            continue
        name = TEAMS[t]
        grp = "top three" if t != 1119 else "meow"
        big = "map > 1200 cells" if d["w"] * d["h"] > 1200 else "map <= 1200 cells"
        ch = [c for c in d3["chances"] if c[1] == s]
        g = games[(name, big)]
        g[0] += 1
        g[1] += bool(ch)
        g[2] += len(ch)
        g[3] += sum(c[5] for c in ch)
        qd = d["sides"][o]["qdeath"]
        killed = bool(qd and qd["reason"] == "headon" and qd["killer"] and qd["killer"]["team"] == s)
        g[4] += killed and not any(c[5] for c in ch)
        seen = set()
        for r, _, did, n, steps, taken, qlen, is_long, own_q in ch:
            free = -(-n // 4)
            paid = max(0, steps - free)
            for G in {grp, name}:           # a set: for meow the group and the name are the same key
                by_len[(G, lc(n))][0] += 1
                by_len[(G, lc(n))][1] += taken
            by_steps[(grp, lc(n), min(steps, 5))][0] += 1
            by_steps[(grp, lc(n), min(steps, 5))][1] += taken
            by_paid[(grp, "free steps only" if paid == 0 else f"{min(paid, 4)} paid")][0] += 1
            by_paid[(grp, "free steps only" if paid == 0 else f"{min(paid, 4)} paid")][1] += taken
            by_map[(grp, big, "short attacker (<=4)" if n <= 4 else "attacker 5-12")][0] += 1
            by_map[(grp, big, "short attacker (<=4)" if n <= 4 else "attacker 5-12")][1] += taken
            ph = ("r<150" if r < 150 else "r150-299" if r < 300 else "r300-399" if r < 400 else "r400+")
            by_phase[(grp, ph, "own queen alive" if own_q else "own queen dead")][0] += 1
            by_phase[(grp, ph, "own queen alive" if own_q else "own queen dead")][1] += taken
            by_leader[(grp, "team's longest" if is_long else "not the longest", "her len<=4" if qlen <= 4 else "her len 5+")][0] += 1
            by_leader[(grp, "team's longest" if is_long else "not the longest", "her len<=4" if qlen <= 4 else "her len 5+")][1] += taken
            if did not in seen:          # first chance of each dragon in this game
                seen.add(did)
                first[(grp, lc(n))][0] += 1
                first[(grp, lc(n))][1] += any(c[5] for c in ch if c[2] == did)

print("=== chances per game and how many were taken")
for k in sorted(games):
    g = games[k]
    print(f"  {k[0]:9s} {k[1]:18s} games {g[0]:3d}  with a chance {g[1] / g[0]:.2f}  chances/game {g[2] / g[0]:5.2f}  taken {g[3]:4d} ({g[3] / max(1, g[2]):.3f} of chances)  "
          f"queen kills with no flagged chance {g[4]}")
print("\n=== share of chances taken, by attacker length (chance-turns)")
for G in ("top three", "Vibing++", "SSS", "forgot", "meow"):
    print(f"  {G:9s} " + " | ".join(f"{c}: {rate(by_len[(G, c)])}" for c in ("L2", "L3", "L4", "L5-9", "L10-12")))
print("\n=== the same, counting each dragon once (did it ever take one of its chances in that game?)")
for G in ("top three", "meow"):
    print(f"  {G:9s} " + " | ".join(f"{c}: {rate(first[(G, c)])}" for c in ("L2", "L3", "L4", "L5-9", "L10-12")))
print("\n=== by steps needed")
for G in ("top three", "meow"):
    for c in ("L2", "L3", "L4", "L5-9", "L10-12"):
        cells = [f"{st} step{'s' if st > 1 else ''}{'+' if st == 5 else ''}: {rate(by_steps[(G, c, st)])}" for st in (1, 2, 3, 4, 5) if by_steps[(G, c, st)][0]]
        print(f"  {G:9s} {c:6s} " + " | ".join(cells))
print("\n=== by paid steps needed (segments the attacker gives up)")
for G in ("top three", "meow"):
    print(f"  {G:9s} " + " | ".join(f"{k}: {rate(by_paid[(G, k)])}" for k in ("free steps only", "1 paid", "2 paid", "3 paid", "4 paid")))
print("\n=== by map class and attacker class")
for k in sorted(by_map):
    print(f"  {k[0]:9s} {k[1]:18s} {k[2]:22s} {rate(by_map[k])}")
print("\n=== by phase and own queen")
for k in sorted(by_phase):
    print(f"  {k[0]:9s} {k[1]:9s} {k[2]:16s} {rate(by_phase[k])}")
print("\n=== by whether the attacker is its team's longest dragon, and her length")
for k in sorted(by_leader):
    print(f"  {k[0]:9s} {k[1]:16s} {k[2]:11s} {rate(by_leader[k])}")
