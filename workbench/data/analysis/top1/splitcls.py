#!/usr/bin/env python3
"""Splits per 50 rounds by parent length class, large and medium maps, per team (opp elo >= 2000). Reads timeline.csv."""
import csv
from collections import defaultdict

TOP = {"306": "Vibing++", "91": "SSS", "264": "forgot", "1119": "meow"}
games = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
acc = defaultdict(lambda: [0.0, 0.0, 0.0, 0, 0.0, 0.0])
for r in csv.DictReader(open("timeline.csv")):
    g = games[r["game_id"]]
    if r["team_id"] not in TOP:
        continue
    o = "B" if r["side"] == "A" else "A"
    if not g[f"team{o}Elo"] or float(g[f"team{o}Elo"]) < 2000:
        continue
    sz = "large" if g["map_size"].startswith("large") else "medium" if g["map_size"].startswith("medium") else "small"
    if r["bucket"] not in ("100", "150", "200", "250", "300", "350"):
        continue
    a = acc[(sz, TOP[r["team_id"]], int(r["bucket"]))]
    a[0] += int(r["splits_le4"])
    a[1] += int(r["splits_5_9"])
    a[2] += int(r["splits_10plus"])
    a[3] += 1
    a[4] += int(r["deaths_le4"])
    a[5] += int(r["units"])
for sz in ("large", "medium"):
    print(f"=== {sz}: splits per 50 rounds by parent length (<=4 | 5-9 | 10+), deaths of <=4-long, units at bucket end")
    for name in TOP.values():
        line = []
        for b in (100, 150, 200, 250, 300, 350):
            a = acc[(sz, name, b)]
            if a[3]:
                line.append(f"r{b - 50}-{b}: {a[0] / a[3]:4.1f} {a[1] / a[3]:4.1f} {a[2] / a[3]:4.1f} d{a[4] / a[3]:4.1f} u{a[5] / a[3]:4.1f}")
        print(f"{name:9s} " + " | ".join(line))
