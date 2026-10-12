#!/usr/bin/env python3
"""Games that reach round 500 with both queens alive: queen lengths, who wins, by what."""
import csv
from collections import Counter, defaultdict

TOP = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}
games = list(csv.DictReader(open("games.csv")))
for team, name in TOP.items():
    print(f"\n== {name}: r500 games with both queens alive (opp elo >= 2000)")
    bymap = defaultdict(list)
    for g in games:
        for s in "AB":
            if int(g[f"team{s}Id"]) != team:
                continue
            o = "B" if s == "A" else "A"
            if not g[f"team{o}Elo"] or float(g[f"team{o}Elo"]) < 2000 or g["end_type"] == "wipe-out":
                continue
            a, b = int(g[f"final_queen_length_{s}"]), int(g[f"final_queen_length_{o}"])
            if a > 0 and b > 0:
                bymap[g["map"]].append((a, b, g["winner"] == s, g["end_type"], int(g[f"final_longest_length_{s}"]),
                                        int(g[f"final_longest_length_{o}"]), g["game_id"], g[f"team{o}Name"][:10]))
    tie = Counter()
    for m, v in sorted(bymap.items()):
        ties = [x for x in v if x[0] == x[1]]
        tie["tie"] += len(ties)
        tie["all"] += len(v)
        tie["tieW"] += sum(x[2] for x in ties)
        print(f"  {m:18s} n={len(v):2d} ties={len(ties):2d} | " + " ".join(
            f"{a}v{b}{'W' if w else 'L'}" for a, b, w, *_ in sorted(v)[:40]))
    print("  total", dict(tie))
    if team == 1119:
        for m, v in sorted(bymap.items()):
            for x in v:
                print("   ", m, x)
