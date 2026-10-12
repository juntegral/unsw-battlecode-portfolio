#!/usr/bin/env python3
"""c_pick.py [map substring ...]: list candidate games per map for sub-session A3 (read-only).

For each map: our games (team 1119) against 2000+ opponents with side, opponent, result, end type, final units /
total / longest, date; then games of forgot (264), SSS (91), Vibing++ (306) on the same map with the side letter of
each, marking games against test4 (19) and WeHaveQuizzes (87).
"""
import csv
import sys
from collections import Counter, defaultdict

GAMES = list(csv.DictReader(open("games.csv")))
want = [a.lower() for a in sys.argv[1:]]
TOP = {306: "Vibing++", 91: "SSS", 264: "forgot", 1119: "meow"}


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


bymap = defaultdict(list)
for g in GAMES:
    bymap[g["map"]].append(g)

for m in sorted(bymap):
    if want and not any(w in m.lower() for w in want):
        continue
    gs = bymap[m]
    g0 = gs[0]
    print(f"\n######## {m} | {g0['width']}x{g0['height']} = {g0['cells']} cells | {g0['map_size']} | {len(gs)} games in games.csv")
    for team in (1119, 264, 91, 306):
        rows = []
        for g in gs:
            for s in "AB":
                if int(g[f"team{s}Id"]) != team:
                    continue
                o = "B" if s == "A" else "A"
                if fnum(g[f"team{o}Elo"]) < 2000:
                    continue
                rows.append((g, s, o))
        wins = sum(1 for g, s, o in rows if g["winner"] == s)
        sides = Counter(s for g, s, o in rows)
        print(f"  -- {TOP[team]} ({team}): {len(rows)} games vs 2000+, {wins} wins; sides {dict(sides)}")
        if not want:
            continue
        for g, s, o in sorted(rows, key=lambda t: t[0]["completed_at"]):
            res = "W" if g["winner"] == s else "L"
            flag = ""
            oid = int(g[f"team{o}Id"])
            if oid in (19, 87):
                flag = " <== our usual opponent"
            if oid in TOP:
                flag = f" <== vs {TOP[oid]}"
            print(f"     {g['game_id']} {g['completed_at'][:16]} side {s} {res} {g['end_type']:10s} r{g['rounds']:>3s} "
                  f"own {g[f'final_units_{s}']:>2s}u/{g[f'final_total_length_{s}']:>3s}t/{g[f'final_longest_length_{s}']:>3s}L/q{g[f'final_queen_length_{s}']:>2s} "
                  f"opp {g[f'final_units_{o}']:>2s}u/{g[f'final_total_length_{o}']:>3s}t/{g[f'final_longest_length_{o}']:>3s}L/q{g[f'final_queen_length_{o}']:>2s} "
                  f"vs {g[f'team{o}Name'][:18]:18s} ({oid}, {fnum(g[f'team{o}Elo']):.0f}){flag}")
