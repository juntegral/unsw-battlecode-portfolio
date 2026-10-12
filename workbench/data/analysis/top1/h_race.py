#!/usr/bin/env python3
"""The longest-dragon race (round-500 games in which both queens ended dead).  Output: stdout -> h_out/race.txt

1. Win rate by own / enemy total length at round 400 (bands) and by own / enemy longest dragon at round 400,
   for meow, the live bot and the three top teams: is our conversion worse at the same state?
2. What predicts the result: a logistic fit of the win on log(longest ratio at round 400) and log(total ratio at
   round 400), per group.  (Does the leader's length at round 400 matter more than the team's total?)
3. Growth of the longest dragon from round 300 to 400 and from 400 to the end, own and enemy.
4. Round at which the own longest dragon first reaches 15 and 20.
"""
import json
import math
from collections import defaultdict

rows = json.load(open("h_out/base.json"))
q = {}


def grp(r):
    g = []
    if "meow" in r["groups"]:
        g.append("meow")
        if r["build"] == "live":
            g.append("meow live")
    for t in ("Vibing++", "SSS", "forgot"):
        if t in r["groups"]:
            g.append(t)
            g.append("top3")
    if "opp_of_meow" in r["groups"]:
        g.append("opp of meow")
    return g


dd = [r for r in rows if r["end_type"] != "wipe-out" and not r["my_fin"]["queen"] and not r["op_fin"]["queen"]
      and r.get("my_tot400") and r.get("op_tot400")]
G = ["meow", "meow live", "opp of meow", "Vibing++", "SSS", "forgot", "top3"]
B = [0, 0.5, 0.8, 1.25, 2.0, 1e9]
names = ["<0.5", "0.5-0.8", "0.8-1.25", "1.25-2", ">2"]


def bi(x):
    for i in range(len(B) - 1):
        if B[i] <= x < B[i + 1]:
            return i


print("== 1. Round-500 games with both queens dead: wins / games ==")
for label, key in (("own / enemy TOTAL length at round 400", "tot"), ("own / enemy LONGEST dragon at round 400", "lon")):
    print(f"-- by {label}: " + " | ".join(names))
    for g in G:
        c = defaultdict(lambda: [0, 0])
        for r in dd:
            if g not in grp(r):
                continue
            x = r[f"my_{key}400"] / max(1, r[f"op_{key}400"])
            c[bi(x)][0] += 1
            c[bi(x)][1] += r["win"]
        n = sum(v[0] for v in c.values())
        w = sum(v[1] for v in c.values())
        print(f"   {g:12s} {w:3d}/{n:3d} = {100 * w / max(1, n):3.0f}%   " + " | ".join(f"{c[i][1]}/{c[i][0]}" for i in range(5)))

print("\n== 2. Logistic fit: win ~ a + b1*log(longest ratio r400) + b2*log(total ratio r400) ==")
for g in G:
    xs = [(math.log(max(1, r["my_lon400"]) / max(1, r["op_lon400"])), math.log(r["my_tot400"] / r["op_tot400"]), r["win"]) for r in dd if g in grp(r)]
    if len(xs) < 30:
        continue
    a = b1 = b2 = 0.0
    for _ in range(100):
        g_ = [0.0] * 3
        h = [[0.0] * 3 for _ in range(3)]
        for x1, x2, y in xs:
            z = a + b1 * x1 + b2 * x2
            p = 1 / (1 + math.exp(-max(-30, min(30, z))))
            v = [1.0, x1, x2]
            for i in range(3):
                g_[i] += (y - p) * v[i]
                for j in range(3):
                    h[i][j] += p * (1 - p) * v[i] * v[j]
        # solve h * d = g_ (3x3, Gaussian elimination) with a small ridge
        for i in range(3):
            h[i][i] += 1e-6
        m = [h[i][:] + [g_[i]] for i in range(3)]
        for i in range(3):
            piv = m[i][i]
            for j in range(i, 4):
                m[i][j] /= piv
            for k in range(3):
                if k != i:
                    f = m[k][i]
                    for j in range(i, 4):
                        m[k][j] -= f * m[i][j]
        d = [m[i][3] for i in range(3)]
        a, b1, b2 = a + d[0], b1 + d[1], b2 + d[2]
        if max(abs(x) for x in d) < 1e-8:
            break
    print(f"   {g:12s} n={len(xs):3d}  intercept {a:+.2f}  longest-ratio {b1:+.2f}  total-ratio {b2:+.2f}")

print("\n== 3. Longest dragon, means over these games: own r300 -> r400 -> end | enemy r300 -> r400 -> end ==")
for g in G:
    xs = [r for r in dd if g in grp(r) and r.get("my_lon300")]
    if not xs:
        continue
    n = len(xs)
    m = lambda k: sum(r[k] for r in xs) / n
    print(f"   {g:12s} n={n:3d}  own {m('my_lon300'):5.1f} -> {m('my_lon400'):5.1f} -> {sum(r['my_fin']['longest'] for r in xs) / n:5.1f} | "
          f"enemy {m('op_lon300'):5.1f} -> {m('op_lon400'):5.1f} -> {sum(r['op_fin']['longest'] for r in xs) / n:5.1f} | "
          f"own total r400 {m('my_tot400'):5.0f} vs {m('op_tot400'):5.0f}; own units r400 {m('my_uni400'):4.1f} vs {m('op_uni400'):4.1f}")

print("\n== 4. Level games (total ratio at r400 0.8-1.25): longest at r400 and the result ==")
for g in G:
    xs = [r for r in dd if g in grp(r) and 0.8 <= r["my_tot400"] / r["op_tot400"] < 1.25]
    if not xs:
        continue
    n = len(xs)
    w = sum(r["win"] for r in xs)
    ahead = [r for r in xs if r["my_lon400"] > r["op_lon400"]]
    behind = [r for r in xs if r["my_lon400"] <= r["op_lon400"]]
    print(f"   {g:12s} {w}/{n}; own longest ahead at r400: {sum(r['win'] for r in ahead)}/{len(ahead)}; not ahead: {sum(r['win'] for r in behind)}/{len(behind)};"
          f" mean own longest r400 {sum(r['my_lon400'] for r in xs) / n:.1f} vs {sum(r['op_lon400'] for r in xs) / n:.1f}")
