#!/usr/bin/env python3
"""Who is rank 1, sample sizes, head-to-head and map results. Reads games.csv only."""
import csv
from collections import Counter, defaultdict

TOP = {306: "Vibing++", 91: "SSS", 264: "forgot"}
US = 1119

games = list(csv.DictReader(open("games.csv")))
print("games", len(games))
latest = {}
for g in games:
    for s in "AB":
        t = int(g[f"team{s}Id"])
        if g[f"team{s}Elo"]:
            k = (g["completed_at"], int(g["game_id"]))
            if t not in latest or k > latest[t][0]:
                latest[t] = (k, float(g[f"team{s}Elo"]), g[f"team{s}Name"])
rank = sorted(latest.items(), key=lambda kv: -kv[1][1])[:14]
print("\nlatest observed elo (collected games):")
for t, (k, elo, name) in rank:
    print(f"  {t:5d} {name[:28]:28s} {elo:7.0f}  last {k[0]}")


def rows_for(team, min_opp=2000):
    out = []
    for g in games:
        for s in "AB":
            if int(g[f"team{s}Id"]) != team:
                continue
            o = "B" if s == "A" else "A"
            oe = float(g[f"team{o}Elo"]) if g[f"team{o}Elo"] else 0
            if oe < min_opp:
                continue
            out.append(dict(g=g, side=s, opp=int(g[f"team{o}Id"]), opp_elo=oe, win=g["winner"] == s,
                            size=g["map_size"], map=g["map"], end=g["end_type"]))
    return out


for team, name in list(TOP.items()) + [(US, "meow")]:
    rs = rows_for(team)
    w = sum(r["win"] for r in rs)
    print(f"\n== {name} ({team}) vs elo>=2000: {w}/{len(rs)} = {w / max(1, len(rs)):.3f}")
    by = defaultdict(lambda: [0, 0])
    for r in rs:
        by[r["size"]][0] += r["win"]
        by[r["size"]][1] += 1
    print("  by size:", {k: f"{v[0]}/{v[1]}={v[0] / v[1]:.2f}" for k, v in sorted(by.items())})
    by = defaultdict(lambda: [0, 0])
    for r in rs:
        by[r["map"]][0] += r["win"]
        by[r["map"]][1] += 1
    print("  by map:", ", ".join(f"{k} {v[0]}/{v[1]}" for k, v in sorted(by.items())))
    wt = Counter(r["end"] for r in rs if r["win"])
    lt = Counter(r["end"] for r in rs if not r["win"])
    print("  win types:", dict(wt), " loss types:", dict(lt))
    by = defaultdict(lambda: [0, 0])
    for r in rs:
        if r["opp"] in TOP or r["opp"] == US:
            by[r["opp"]][0] += r["win"]
            by[r["opp"]][1] += 1
    print("  head to head:", {TOP.get(k, "meow"): f"{v[0]}/{v[1]}" for k, v in by.items()})
    opp = Counter(r["opp"] for r in rs)
    print("  opponents:", len(opp), "most common", opp.most_common(8))
    dates = sorted(r["g"]["completed_at"] for r in rs)
    print("  dates", dates[0], "..", dates[-1])
