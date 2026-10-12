#!/usr/bin/env python3
"""Unit counts by length class over time, per team and map size (sealed map included: the economy does not depend on the queen).

Also: our large-map vs medium-map trajectories around our split-stop rounds (150 on maps > 1200 cells, 300 otherwise).
Reads q/*.json. Opp elo >= 2000.
"""
import glob
import json
from collections import defaultdict

TOP = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}
games = [json.load(open(f)) for f in glob.glob("q/*.json")]


def size(d):
    c = d["w"] * d["h"]
    return "small" if c <= 700 else "medium" if c <= 1500 else "large"


for sz in ("large", "medium"):
    print(f"=== {sz} maps: mean number of dragons by length class (2 | 3-4 | 5-9 | 10-19 | 20+) and units, at rounds 100..400")
    for team, name in TOP.items():
        for res in ("all", "W", "L"):
            acc = defaultdict(lambda: [0.0] * 6)
            for d in games:
                if size(d) != sz:
                    continue
                for s in "AB":
                    o = "B" if s == "A" else "A"
                    if d["sides"][s]["team"] != team or (d["sides"][o]["elo"] or 0) < 2000:
                        continue
                    if res != "all" and (d["winner"] == s) != (res == "W"):
                        continue
                    for row in d["sides"][s]["per"]["lenhist"]:
                        if row[0] in (100, 150, 200, 250, 300, 400):
                            a = acc[row[0]]
                            for k in range(5):
                                a[k] += row[1 + k]
                            a[5] += 1
            if team != 1119 and res != "all":
                continue
            line = []
            for r in (100, 150, 200, 250, 300, 400):
                a = acc[r]
                if a[5]:
                    line.append(f"r{r}: " + " ".join(f"{a[k] / a[5]:4.1f}" for k in range(5)) + f" ={sum(a[:5]) / a[5]:4.1f}")
            print(f"{name:9s} {res:3s} " + " | ".join(line))
