#!/usr/bin/env python3
"""d_list.py <team_id|opp> [maxround] [map substring]: one line per queen death of a team from q/*.json (sub-session A4).

Opponents rated 2000+, Schooltime left out.  'opp' = the opponents of meow in meow's games.
Columns: game, map, cells, run, side, opponent, result/end type, death round, reason, length, position, free cells and
openness at the start of the fatal round, the killer (length, steps), last split before death.
"""
import csv
import json
import sys

who = sys.argv[1]
maxr = int(sys.argv[2]) if len(sys.argv) > 2 else 999
sub = sys.argv[3] if len(sys.argv) > 3 else ""
rows = []
for g in csv.DictReader(open("games.csv")):
    if g["map"] == "Schooltime" or sub.lower() not in g["map"].lower():
        continue
    for s in "AB":
        o = "B" if s == "A" else "A"
        if who == "opp":
            if g[f"team{o}Id"] != "1119" or not g[f"team{s}Elo"] or float(g[f"team{s}Elo"]) < 2000:
                continue
        elif g[f"team{s}Id"] != who or not g[f"team{o}Elo"] or float(g[f"team{o}Elo"]) < 2000:
            continue
        q = json.load(open(f"q/{g['game_id']}.json"))
        sd = q["sides"][s]
        qd = sd["qdeath"]
        if not qd or qd["round"] >= maxr:
            continue
        k = qd.get("killer")
        last = qd.get("last") or []
        sp = [x for x in sd["qsplits"] if x[0] <= qd["round"]]
        rows.append((g["map"], qd["round"], f"{g['game_id']} {g['map'][:14]:14s} {g['cells']:>4s} {g['battle_id'][:18]:18s} {s} vs {g['team' + o + 'Name'][:10]:10s} "
                     f"{'W' if g['winner'] == s else 'L'} {g['end_type'][:9]:9s} r{qd['round']:3d} {qd['reason']:8s} L{qd['len']} at {qd['pos']} "
                     f"free {last[11] if last else '-'} ball {last[12] if last else '-'} deg {last[13] if last else '-'} a3 {last[7] if last else '-'} e4 {last[5] if last else '-'} "
                     + (f"killer L{k['len']} {k['steps_used']}st born {int(k['born_this_round'])}" if k else "own action" if qd['own_action'] else "")
                     + (f" | last split r{sp[-1][0]} {sp[-1][1]}->{sp[-1][2]}+{sp[-1][3]}" if sp else " | no split")))
rows.sort()
for r in rows:
    print(r[2])
print(len(rows), "deaths")
