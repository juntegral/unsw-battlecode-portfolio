#!/usr/bin/env python3
"""Our queen's self-inflicted deaths (wall / own body / another body / she rams a head) on the ladder.

1. Share of games by team (opp elo >= 2000), with 'noaction' (a dragon killing itself on purpose or by a bad order) shown apart.
2. What those games became (wipe-out, round-500 by queen state) and a what-if: had she not crashed and then
   survived as often as a top-three queen does on the same map.
3. The state at the start of the fatal round: length, free neighbour cells, openness (ball4), allied heads within 3,
   nearest small enemy, distance from spawn, and whether our queen rules were on (map > 600 cells).
Reads q/*.json.
"""
import glob
import json
import statistics
from collections import Counter, defaultdict

TOP3 = {306: "Vibing++", 91: "SSS", 264: "forgot"}
SEALED = {"Schooltime"}
games = [json.load(open(f)) for f in glob.glob("q/*.json")]
SELF = ("wall", "self", "body", "own_ram", "ally_ram")


def cause(sd, s):
    qd = sd["qdeath"]
    if qd is None:
        return "alive"
    r = qd["reason"]
    if r == "headon":
        return "own_ram" if qd["killer"] is None else "ally_ram" if qd["killer"]["team"] == s else "rammed"
    return r


def sides(team):
    for d in games:
        if d["map"] in SEALED:
            continue
        for s in "AB":
            o = "B" if s == "A" else "A"
            if d["sides"][s]["team"] == team and (d["sides"][o]["elo"] or 0) >= 2000:
                yield d, s, o


print("=== 1. how the own queen ends, share of games (sealed map excluded)")
alive_by_map = defaultdict(lambda: [0, 0])
for team, name in list(TOP3.items()) + [(1119, "meow")]:
    c = Counter()
    n = 0
    early = []
    for d, s, o in sides(team):
        n += 1
        k = cause(d["sides"][s], s)
        c["self-inflicted" if k in SELF else k] += 1
        if k in SELF:
            c["  " + k] += 1
            early.append(d["sides"][s]["qdeath"]["round"])
        if team in TOP3:
            alive_by_map[d["map"]][0] += k == "alive"
            alive_by_map[d["map"]][1] += 1
    print(f"{name:9s} n={n:3d} " + " ".join(f"{k.strip()}={v / n:.3f}" for k, v in sorted(c.items(), key=lambda kv: -kv[1]))
          + f" | median round of a self-inflicted death {statistics.median(early) if early else '-'}")

print("\n=== 2. our games with a self-inflicted queen death: what they became, and the what-if")
out = Counter()
exp_flips = 0.0
exp_by_map = defaultdict(float)
n_by_map = Counter()
for d, s, o in sides(1119):
    k = cause(d["sides"][s], s)
    if k not in SELF:
        continue
    n_by_map[d["map"]] += 1
    win = d["winner"] == s
    if d["end_type"] == "wipe-out":
        out["wipe-out " + ("W" if win else "L")] += 1
        continue
    oq = d["sides"][o]["final"]["queen"]
    key = "r500 their queen " + ("alive" if oq else "dead") + (" W" if win else " L")
    out[key] += 1
    if not win and not oq:
        a = alive_by_map[d["map"]]
        p = a[0] / a[1] if a[1] else 0
        exp_flips += p
        exp_by_map[d["map"]] += p
print(" ", dict(sorted(out.items())))
print(f"  round-500 losses with both queens dead after she crashed: {out['r500 their queen dead L']} "
      f"(each would be a queen-rule WIN had she lived)")
print(f"  expected wins if she had not crashed and then survived like a top-three queen on that map: {exp_flips:.1f}")
print("  by map (games with a self-inflicted death -> expected flips):",
      {m: f"{n_by_map[m]} -> {exp_by_map[m]:.1f}" for m in sorted(n_by_map)})

print("\n=== 3. state at the start of the fatal round (our queen, self-inflicted deaths)")
rows = []
for d, s, o in sides(1119):
    sd = d["sides"][s]
    k = cause(sd, s)
    if k not in SELF:
        continue
    last = sd["qdeath"]["last"]
    cells = d["w"] * d["h"]
    rows.append(dict(k=k, map=d["map"], r=sd["qdeath"]["round"], len=sd["qdeath"]["len"], free=last[11], ball=last[12],
                     deg=last[13], a3=last[7], a6=last[6], e4=last[5], small=last[10], home=last[15], rules=cells > 600,
                     qsteps=sd["qdeath"]["qsteps_this_round"], gid=d["game_id"]))
n = len(rows)
print("n =", n)
print("  cause:", dict(Counter(r["k"] for r in rows)))
print("  queen rules on (map > 600 cells):", dict(Counter(r["rules"] for r in rows)))
print("  length at death:", dict(sorted(Counter(r["len"] for r in rows).items())))
print("  free neighbour cells at round start:", dict(sorted(Counter(r["free"] for r in rows).items())))
print("  open exits of the cell (kelp only):", dict(sorted(Counter(r["deg"] for r in rows).items())))
print("  openness ball4 (41 = open field): <=10:", sum(r["ball"] <= 10 for r in rows), " 11-20:", sum(10 < r["ball"] <= 20 for r in rows), " >20:", sum(r["ball"] > 20 for r in rows))
print("  allied heads within 3 steps:", dict(sorted(Counter(min(r["a3"], 3) for r in rows).items())))
print("  small enemy head within 3 steps:", sum(1 for r in rows if r["small"] is not None and r["small"] <= 3), " within 6:", sum(1 for r in rows if r["small"] is not None and r["small"] <= 6))
print("  steps she had already taken in the fatal turn:", dict(sorted(Counter(r["qsteps"] for r in rows).items())))
print("  median round", statistics.median(r["r"] for r in rows), " median distance from spawn", statistics.median(r["home"] for r in rows))
tab = Counter()
for r in rows:
    box = "no free cell" if r["free"] == 0 else "1 free cell" if r["free"] == 1 else "2+ free cells"
    tab[(r["k"], box)] += 1
print("  cause x free cells:", {f"{k[0]} / {k[1]}": v for k, v in sorted(tab.items())})
print("  examples (game, map, round, cause, len, free, ball4, allies<=3):")
for r in sorted(rows, key=lambda r: (r["map"], r["r"]))[:60]:
    print(f"    {r['gid']} {r['map']:16s} r{r['r']:3d} {r['k']:8s} L{r['len']} free{r['free']} ball{r['ball']:2d} a3={r['a3']} e4={r['e4']} home{r['home']}")
