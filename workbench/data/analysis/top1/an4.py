#!/usr/bin/env python3
"""Turn-level ram chances on the enemy queen, with the in-view flag (q3v2/*.json from extract3.py).
Opp elo >= 2000, sealed map (Schooltime) excluded.

chance   = at the start of a non-queen dragon's own turn there is a path of free cells from its head to the enemy
           queen's head no longer than its one-turn reach (dragons longer than 12 skipped)
in view  = her head is inside the 7x7 square around the attacker's head at that moment
taken    = the dragon rammed her that turn
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


def lc(n):
    return "L2-3" if n <= 3 else "L4" if n == 4 else "L5-9" if n <= 9 else "L10-12"


def rate(t):
    return f"{t[1]:4d}/{t[0]:5d} = {t[1] / t[0]:.3f}" if t[0] else "    -"


view = defaultdict(lambda: [0, 0])
paid_view = defaultdict(lambda: [0, 0])
mapcls = defaultdict(lambda: [0, 0])
games = defaultdict(lambda: [0, 0, 0, 0, 0])
missed = defaultdict(lambda: [0, 0])
others = defaultdict(lambda: [0, 0])
for gid, d in Q.items():
    try:
        d3 = json.load(open(f"q3v2/{gid}.json"))
    except FileNotFoundError:
        continue
    for s in "AB":
        o = "B" if s == "A" else "A"
        t = d["sides"][s]["team"]
        ch = [c for c in d3["chances"] if c[1] == s]
        if (d["sides"][o]["elo"] or 0) >= 2000 and t not in TEAMS and "top1" in d["sources"]:
            for c in ch:
                k = ("other 2000+ teams", "in view" if c[9] else "not in view", lc(c[3]))
                others[k][0] += 1
                others[k][1] += c[5]
        if t not in TEAMS or (d["sides"][o]["elo"] or 0) < 2000:
            continue
        name = TEAMS[t]
        big = ">1200 cells" if d["w"] * d["h"] > 1200 else "<=1200 cells"
        g = games[(name, big)]
        g[0] += 1
        iv = [c for c in ch if c[9]]
        g[1] += bool(iv)
        g[2] += len(iv)
        g[3] += sum(c[5] for c in iv)
        g[4] += bool(iv) and not any(c[5] for c in ch)
        for r, _, did, n, steps, taken, qlen, is_long, own_q, inview in ch:
            free = -(-n // 4)
            paid = max(0, steps - free)
            v = "in view" if inview else "not in view"
            view[(name, v, lc(n))][0] += 1
            view[(name, v, lc(n))][1] += taken
            view[(name, v, "all")][0] += 1
            view[(name, v, "all")][1] += taken
            if inview:
                pk = "free" if paid == 0 else f"{min(paid, 4)} paid"
                paid_view[(name, pk)][0] += 1
                paid_view[(name, pk)][1] += taken
                mapcls[(name, big, "longest" if is_long else "not longest")][0] += 1
                mapcls[(name, big, "longest" if is_long else "not longest")][1] += taken
                ph = "r<300" if r < 300 else "r300+"
                missed[(name, ph, "own queen alive" if own_q else "own queen dead")][0] += 1
                missed[(name, ph, "own queen alive" if own_q else "own queen dead")][1] += taken

print("=== chances taken, by whether she was in the attacker's view, and attacker length")
for name in TEAMS.values():
    for v in ("in view", "not in view"):
        print(f"  {name:9s} {v:12s} " + " | ".join(f"{c}: {rate(view[(name, v, c)])}" for c in ("L2-3", "L4", "L5-9", "L10-12", "all")))
print("  other 2000+ teams in the top-team games:")
for v in ("in view", "not in view"):
    print(f"  {'others':9s} {v:12s} " + " | ".join(f"{c}: {rate(others[('other 2000+ teams', v, c)])}" for c in ("L2-3", "L4", "L5-9", "L10-12")))
print("\n=== in-view chances by paid steps needed")
for name in TEAMS.values():
    print(f"  {name:9s} " + " | ".join(f"{k}: {rate(paid_view[(name, k)])}" for k in ("free", "1 paid", "2 paid", "3 paid", "4 paid")))
print("\n=== in-view chances by map class and whether the attacker is its team's longest")
for k in sorted(mapcls):
    print(f"  {k[0]:9s} {k[1]:13s} {k[2]:12s} {rate(mapcls[k])}")
print("\n=== in-view chances by phase and own queen")
for k in sorted(missed):
    print(f"  {k[0]:9s} {k[1]:6s} {k[2]:16s} {rate(missed[k])}")
print("\n=== per game: games with an in-view chance, in-view chances per game, taken, games with an in-view chance and no ram at all")
for k in sorted(games):
    g = games[k]
    print(f"  {k[0]:9s} {k[1]:13s} games {g[0]:3d}  with an in-view chance {g[1]:3d} ({g[1] / g[0]:.2f})  in-view chances/game {g[2] / g[0]:.2f}  taken {g[3]}  had one but never rammed her {g[4]}")
