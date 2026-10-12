#!/usr/bin/env python3
"""d_cnt.py: how many games each of the four teams has against each 2000+ opponent, and per map against test4 / WHQ
(sub-session A4, helper for choosing comparison games).  Schooltime left out."""
import csv
from collections import Counter

T = {"1119": "meow", "306": "Vibing++", "91": "SSS", "264": "forgot"}
c = Counter()
m = Counter()
for g in csv.DictReader(open("games.csv")):
    if g["map"] == "Schooltime":
        continue
    for s in "AB":
        o = "B" if s == "A" else "A"
        if g[f"team{s}Id"] in T and g[f"team{o}Elo"] and float(g[f"team{o}Elo"]) >= 2000:
            c[(T[g[f"team{s}Id"]], g[f"team{o}Name"][:16], g[f"team{o}Id"])] += 1
            if g[f"team{o}Id"] in ("19", "87"):
                m[(T[g[f"team{s}Id"]], g["map"], s)] += 1
for t in T.values():
    print(t, sorted(((v, k[1], k[2]) for k, v in c.items() if k[0] == t), reverse=True)[:14])
print()
maps = sorted({k[1] for k in m})
print("games vs test4 or WeHaveQuizzes by map and side (A/B):")
for mp in maps:
    print(f"  {mp:18s} " + " | ".join(f"{t} A{m[(t, mp, 'A')]} B{m[(t, mp, 'B')]}" for t in T.values()))
