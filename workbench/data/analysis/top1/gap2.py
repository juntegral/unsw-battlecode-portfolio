#!/usr/bin/env python3
"""Compact gap table from timeline.csv: protagonist vs us vs the other two, by phase and map size,
with each top team's own wins vs losses as a control. Opponents rated >= 2000 only. Means over games.

Usage: python3 gap2.py [size ...]   sizes: small medium large (default all three)
"""
import csv
import sys
from collections import defaultdict

TOP = {306: "Vib", 91: "SSS", 264: "fgt", 1119: "meow"}
SZ = {"small<=700": "small", "medium701-1500": "medium", "large>1500": "large"}
BUCKETS = ("50", "100", "150", "200", "300", "400", "end")
games = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
rows = defaultdict(dict)
for r in csv.DictReader(open("timeline.csv")):
    rows[(r["game_id"], r["side"])][r["bucket"]] = r


def val(r, m):
    if m == "splits":
        return sum(int(r[f"splits_{c}"]) for c in ("le4", "5_9", "10plus"))
    if m == "deaths":
        return sum(int(r[f"deaths_{c}"]) for c in ("le4", "5_9", "10plus"))
    if m == "headon_init":
        return sum(int(r[f"headon_initiated_{c}"]) for c in ("le4", "5_9", "10plus"))
    if m == "sprints":
        return sum(int(r[f"sprints_{c}"]) for c in ("le4", "5_9", "10plus"))
    if m == "trapped":
        return int(r["deaths_wall"]) + int(r["deaths_self"]) + int(r["deaths_body"])
    if m == "pearls":
        return int(r["pearls_natural"]) + int(r["pearls_corpse"])
    v = r[m]
    return float(v) if v not in ("", "NA", "None") else None


METRICS = ("units", "total_length", "longest_length", "queen_alive", "queen_length", "cells_visited", "pearls_natural",
           "pearls_corpse", "splits", "deaths", "trapped", "deaths_headon", "deaths_other", "headon_init", "sprints",
           "portal_crossings", "queen_nearest_enemy_distance", "queen_teammates_within6", "queen_start_distance")


def collect(team, size, result=None):
    out = []
    for g in games.values():
        if SZ[g["map_size"]] != size:
            continue
        for s in "AB":
            if int(g[f"team{s}Id"]) != team:
                continue
            o = "B" if s == "A" else "A"
            if not g[f"team{o}Elo"] or float(g[f"team{o}Elo"]) < 2000:
                continue
            if result is not None and (g["winner"] == s) != result:
                continue
            out.append((rows[(g["game_id"], s)], rows[(g["game_id"], o)]))
    return out


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def fmt(x):
    return "   -  " if x is None else f"{x:6.1f}" if abs(x) < 1000 else f"{x:6.0f}"


for size in (sys.argv[1:] or ["small", "medium", "large"]):
    print(f"\n==================== {size} maps (opp elo >= 2000) ====================")
    groups = []
    for team, name in TOP.items():
        groups.append((name, collect(team, size)))
        if team != 1119:
            groups.append((name + "W", collect(team, size, True)))
            groups.append((name + "L", collect(team, size, False)))
        else:
            groups.append((name + "W", collect(team, size, True)))
            groups.append((name + "L", collect(team, size, False)))
            groups.append(("meow-opp", [(b, a) for a, b in collect(team, size)]))
    print("groups:", ", ".join(f"{n}={len(v)}" for n, v in groups))
    for m in METRICS:
        print(f"\n{m}")
        print("  bucket " + " ".join(f"{n:>8s}" for n, _ in groups))
        for b in BUCKETS:
            line = []
            for n, v in groups:
                line.append(fmt(mean(val(a[b], m) for a, _ in v if b in a)))
            print(f"  r{b:5s} " + " ".join(f"{x:>8s}" for x in line))
