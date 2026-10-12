#!/usr/bin/env python3
"""d_pick.py <map substring> [side]: top-team games on a map, for choosing comparison games (sub-session A4).

One line per game of Vibing++ / SSS / forgot against a 2000+ team on that map: game id, team, its side, the
opponent, result, the team's queen (death round and reason, or alive with final length), whether she was alive at
round 300.  Games against test4 (19) and WeHaveQuizzes (87) are marked with '*', and listed first.
"""
import csv
import json
import sys

T = {"306": "Vibing++", "91": "SSS", "264": "forgot"}
sub = sys.argv[1].lower()
want_side = sys.argv[2] if len(sys.argv) > 2 else None
rows = []
for g in csv.DictReader(open("games.csv")):
    if sub not in g["map"].lower():
        continue
    for s in "AB":
        o = "B" if s == "A" else "A"
        if g[f"team{s}Id"] not in T or not g[f"team{o}Elo"] or float(g[f"team{o}Elo"]) < 2000:
            continue
        if want_side and s != want_side:
            continue
        q = json.load(open(f"q/{g['game_id']}.json"))
        sd = q["sides"][s]
        qd = sd["qdeath"]
        fate = f"alive L{sd['final']['queen']}" if not qd else f"r{qd['round']} {qd['reason']} L{qd['len']}"
        a300 = len(sd["per"]["q"]) > 300 and bool(sd["per"]["q"][300])
        star = "*" if g[f"team{o}Id"] in ("19", "87") else " "
        rows.append((star != "*", g["map"], T[g[f"team{s}Id"]], s,
                     f"{star} {g['game_id']} {g['map'][:15]:15s} {T[g[f'team{s}Id']]:8s} side {s} start {sd['start']} vs {g[f'team{o}Name'][:14]:14s} "
                     f"{'W' if g['winner'] == s else 'L'} {g['end_type'][:10]:10s} rounds {g['rounds']:>3s} | queen {fate:22s} alive r300 {int(a300)} | splits {len(sd['qsplits'])}"))
rows.sort()
for r in rows:
    print(r[4])
