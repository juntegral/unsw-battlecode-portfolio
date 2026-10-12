#!/usr/bin/env python3
"""How games end, by queen state. Reads games.csv + timeline.csv.

For each focus team (vs opponents rated >= 2000): outcome by (own queen alive at end, enemy queen alive at end),
queen survival curve by round, and what decided the game.
"""
import csv
import sys
from collections import Counter, defaultdict

TOP = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}
MIN = 2000
games = {g["game_id"]: g for g in csv.DictReader(open("games.csv"))}
tl = defaultdict(dict)
for r in csv.DictReader(open("timeline.csv")):
    tl[(r["game_id"], r["side"])][r["bucket"]] = r


def rows(team):
    for g in games.values():
        for s in "AB":
            if int(g[f"team{s}Id"]) != team:
                continue
            o = "B" if s == "A" else "A"
            oe = float(g[f"team{o}Elo"]) if g[f"team{o}Elo"] else 0
            if oe >= MIN:
                yield g, s, o


for team, name in TOP.items():
    rs = list(rows(team))
    print(f"\n===== {name} ({team}) vs >={MIN}: N={len(rs)}")
    for size in ("all", "small<=700", "medium701-1500", "large>1500"):
        sub = [(g, s, o) for g, s, o in rs if size == "all" or g["map_size"] == size]
        if not sub:
            continue
        tab = defaultdict(lambda: [0, 0])
        ends = defaultdict(Counter)
        full = 0
        for g, s, o in sub:
            mine, theirs = int(g[f"final_queen_length_{s}"]) > 0, int(g[f"final_queen_length_{o}"]) > 0
            timeout = g["end_type"] != "wipe-out"
            full += timeout
            key = ("wipe" if not timeout else "r500", "ownQ" if mine else "noQ", "theirQ" if theirs else "noQ")
            win = g["winner"] == s
            tab[key][0] += win
            tab[key][1] += 1
            ends[key][g["end_type"] + ("W" if win else "L")] += 1
        w = sum(g["winner"] == s for g, s, o in sub)
        print(f"  -- {size}: N={len(sub)} win {w / len(sub):.2f}; reach r500 {full}/{len(sub)}")
        for key in sorted(tab):
            a, n = tab[key]
            print(f"     {key[0]:5s} own={key[1]:5s} their={key[2]:6s}: {a:3d}/{n:3d} = {a / n:.2f}   {dict(ends[key])}")
        # queen survival curve
        line = []
        for b in ("50", "100", "150", "200", "300", "400", "end"):
            alive = [int(tl[(g["game_id"], s)][b]["queen_alive"]) for g, s, o in sub if b in tl[(g["game_id"], s)]]
            oal = [int(tl[(g["game_id"], o)][b]["queen_alive"]) for g, s, o in sub if b in tl[(g["game_id"], o)]]
            line.append(f"r{b}: {sum(alive) / max(1, len(alive)):.2f}/{sum(oal) / max(1, len(oal)):.2f} (n{len(alive)})")
        print("     queen alive own/opp:", "  ".join(line))
