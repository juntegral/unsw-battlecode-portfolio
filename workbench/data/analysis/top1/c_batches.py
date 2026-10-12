#!/usr/bin/env python3
"""c_batches.py [team_id=1119]: the team's games against 2000+ opponents grouped by battle id (the run they came from).

For each battle id: games, first and last completion time, wins, map sizes, opponents, and the game ids when --ids is given.
The battle id is the only trace in games.csv of which build of the bot played a game.
"""
import csv
import sys
from collections import Counter, defaultdict

team = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 1119
by = defaultdict(list)
for g in csv.DictReader(open("games.csv")):
    if g["map"] == "Schooltime":
        continue
    for s in "AB":
        if int(g[f"team{s}Id"]) != team:
            continue
        o = "B" if s == "A" else "A"
        try:
            if float(g[f"team{o}Elo"]) < 2000:
                continue
        except ValueError:
            continue
        size = "small" if g["map_size"].startswith("small") else "medium" if g["map_size"].startswith("medium") else "large"
        by[g["battle_id"]].append((g["completed_at"], g["game_id"], size, g["map"], g[f"team{o}Name"][:14], g["winner"] == s, g["sources"], s))
print(f"=== BATCHES team {team}: games against 2000+ teams by battle id (Schooltime left out)")
print("battle id | games | first .. last completion | wins | large / medium / small | opponents | sources | side of the team")
for bid, rows in sorted(by.items(), key=lambda kv: min(r[0] for r in kv[1])):
    sizes = Counter(r[2] for r in rows)
    opps = Counter(r[4] for r in rows)
    srcs = Counter(r[6] for r in rows)
    sides = Counter(r[7] for r in rows)
    print(f"{bid:28s} | {len(rows):3d} | {min(r[0] for r in rows)[:16]} .. {max(r[0] for r in rows)[:16]} | {sum(r[5] for r in rows):3d} | "
          f"{sizes['large']} / {sizes['medium']} / {sizes['small']} | {dict(opps)} | {dict(srcs)} | {dict(sides)}")
    if "--ids" in sys.argv:
        print("     " + " ".join(f"{r[1]}({r[3][:6]},{'W' if r[5] else 'L'})" for r in sorted(rows)))
